use log::{error, info};
use lopdf::{
    content::{Content, Operation},
    Document, Error, Object,
};

#[allow(unused_imports)]
use std::{
    collections::BTreeMap,
    io::{Cursor, Read},
};

const APP_NAME: &str = "pdpost-rs-pdf-find-then-colored";

pub fn find_then_colored_text(doc: &mut Document, page_number: u32, text: &str, color_name: &str) -> Result<(), Error> {
    let page = page_number.saturating_sub(1) as usize;
    let page_id = doc
        .page_iter()
        .nth(page)
        .ok_or(Error::PageNumberNotFound(page_number))?;
    let encodings = doc
        .get_page_fonts(page_id)
        .into_iter()
        .map(|(name, font)| (name, font.get_font_encoding().to_owned()))
        .collect::<BTreeMap<Vec<u8>, String>>();
    let content_data = doc.get_page_content(page_id)?;
    let mut content = Content::decode(&content_data)?;
    let mut new_operations = vec![];
    let mut current_encoding = None;
    let mut current_operation_rg = None;
    let mut _current_operation_td = None;
    let mut _current_operation_tf = None;
    let emph_color = match color_name.to_ascii_lowercase().as_str() {
        "black" => (0, 0, 0),
        "blue" => (0, 0, 1),
        "green" => (0, 1, 0),
        "cyan" => (0, 1, 1),
        "fuchsia" => (1, 0, 1),
        "yellow" => (1, 1, 0),
        "white" => (1, 1, 1),
        _ => (1, 0, 0),
    };
    let emph_color_string = format!("{} {} {} rg", emph_color.0, emph_color.1, emph_color.2);
    let emph_ops = Operation::new(&emph_color_string, vec![]);
    for (_ops_idx, operation) in &mut content.operations.iter_mut().enumerate() {
        match operation.operator.as_ref() {
            "Tf" => {
                let current_font = operation
                    .operands
                    .get(0)
                    .ok_or_else(|| Error::Syntax("missing font operand".to_string()))?
                    .as_name()?;
                current_encoding = encodings.get(current_font).map(std::string::String::as_str);
                _current_operation_tf = Some(operation.clone());
                new_operations.push(operation.clone());
            }
            "Td" => {
                _current_operation_td = Some(operation.clone());
                new_operations.push(operation.clone());
            }
            "rg" => {
                current_operation_rg = Some(operation.clone());
                new_operations.push(operation.clone());
            }
            "Tj" => {
                //a string of text
                //let mut _collect_text_string = String::new();
                //collect_text(&mut _collect_text_string, current_encoding, &operation.operands);
                //info!("::->{}", _collect_text_string);
                let mut decoded_text = String::new();
                let mut prefix_text = String::new();
                let mut search_text = String::new();
                let mut suffix_text = String::new();
                let mut found = false;
                for (_str_idx, bytes) in operation.operands.iter_mut().flat_map(Object::as_str_mut).enumerate() {
                    let _decoded_text = Document::decode_text(current_encoding, bytes);
                    decoded_text.push_str(&_decoded_text);
                }
                {
                    if decoded_text.contains(text) {
                        found = true;
                        info!("{} -> {}", _ops_idx, decoded_text);
                        //let new_text = decoded_text.replace(text, other_text);
                        //let encoded_bytes = Document::encode_text(current_encoding, &new_text);
                        //*bytes = encoded_bytes;
                        let start_idx = decoded_text.find(text).unwrap();
                        prefix_text = decoded_text[..start_idx].to_string();
                        search_text = text.to_string();
                        suffix_text = decoded_text[start_idx + text.len()..].to_string();
                    }
                }
                if found {
                    new_operations.push(current_operation_rg.clone().unwrap());
                    new_operations.push(Operation::new("Tj", vec![Object::string_literal(prefix_text)]));
                    new_operations.push(emph_ops.clone());
                    new_operations.push(Operation::new("Tj", vec![Object::string_literal(search_text)]));
                    new_operations.push(current_operation_rg.clone().unwrap());
                    new_operations.push(Operation::new("Tj", vec![Object::string_literal(suffix_text)]));
                } else {
                    new_operations.push(operation.clone());
                }
            }
            "TJ" => {
                //an array of strings
                let mut decoded_text = String::new();
                let mut prefix_text = String::new();
                let mut search_text = String::new();
                let mut suffix_text = String::new();
                let mut found = false;
                for (_arr_idx, arrs) in operation.operands.iter_mut().flat_map(Object::as_array_mut).enumerate() {
                    for (_str_idx, bytes) in arrs.iter_mut().flat_map(Object::as_str_mut).enumerate() {
                        let _decoded_text = Document::decode_text(current_encoding, bytes);
                        decoded_text.push_str(&_decoded_text);
                    }
                    {
                        if decoded_text.contains(text) {
                            found = true;
                            info!("{}/{} ... {}", _ops_idx, _arr_idx, decoded_text);
                            //let new_text = decoded_text.replace(text, other_text);
                            //let encoded_bytes = Document::encode_text(current_encoding, &new_text);
                            //*bytes = encoded_bytes;
                            let start_idx = decoded_text.find(text).unwrap();
                            prefix_text = decoded_text[..start_idx].to_string();
                            search_text = text.to_string();
                            suffix_text = decoded_text[start_idx + text.len()..].to_string();
                        }
                    }
                }
                if found {
                    new_operations.push(current_operation_rg.clone().unwrap());
                    new_operations.push(Operation::new("Tj", vec![Object::string_literal(prefix_text)]));
                    new_operations.push(emph_ops.clone());
                    new_operations.push(Operation::new("Tj", vec![Object::string_literal(search_text)]));
                    new_operations.push(current_operation_rg.clone().unwrap());
                    new_operations.push(Operation::new("Tj", vec![Object::string_literal(suffix_text)]));
                } else {
                    new_operations.push(operation.clone());
                }
            }
            _ => {
                new_operations.push(operation.clone());
            }
        }
    }
    //let modified_content = content.encode()?;
    let modified_content = Content {
        operations: new_operations,
    }
    .encode()?;
    doc.change_page_content(page_id, modified_content)
}

fn main() -> Result<(), Error> {
    let cmd = clap::Command::new(APP_NAME)
        .bin_name(APP_NAME)
        .arg_required_else_help(false)
        .subcommand_required(false)
        .arg(
            clap::arg!(--"input" <PATH>)
                .short('i')
                .value_parser(clap::value_parser!(std::path::PathBuf)),
        )
        .arg(
            clap::arg!(--"output" <PATH>)
                .short('o')
                .value_parser(clap::value_parser!(std::path::PathBuf)),
        )
        .arg(clap::arg!(--"text" <String>).value_parser(clap::value_parser!(String)))
        .arg(
            clap::arg!(--"color" <String>)
                .value_parser(clap::value_parser!(String))
                .default_value("red"),
        )
        .arg(
            clap::arg!(--"font" <String>)
                .value_parser(clap::value_parser!(String))
                .default_value("courier"),
        )
        .arg(
            clap::arg!(--"verbose" <bool>)
                .short('v')
                .help("More detailed logging")
                .value_parser(clap::value_parser!(bool))
                .default_value("true"),
        );
    let matches = cmd.get_matches();

    env_logger::init();
    let verbose = *matches.get_one::<bool>("verbose").unwrap();
    if verbose {
        log::set_max_level(log::LevelFilter::max());
    }

    let input = matches.get_one::<std::path::PathBuf>("input").unwrap();
    if !input.exists() {
        error!("Input file non-exist -> {}", input.to_str().unwrap());
        std::process::exit(1);
    }
    let _output = std::path::PathBuf::from(input.with_extension("ftc.pdf"));
    let output = match matches.get_one::<std::path::PathBuf>("output") {
        Some(file) => file,
        None => &_output,
    };
    let text = matches.get_one::<String>("text").unwrap();
    let color_name = matches.get_one::<String>("color").unwrap();
    info!("Starting up: {}", text);

    let mut doc = Document::load(input).unwrap();

    doc.version = "1.4".to_string();
    find_then_colored_text(&mut doc, 1, text, color_name)?;
    // Store file in current working directory.
    // Note: Line is excluded when running tests
    if true {
        doc.save(output).unwrap();
    }
    Ok(())
}
