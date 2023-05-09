use lopdf::{Document, Object, Error, content::Content};
use log::info;
#[allow(unused_imports)]
use std::{
    collections::BTreeMap,
    io::{Cursor, Read},
};

pub fn replace_text(doc: &mut Document, page_number: u32, text: &str, other_text: &str) -> Result<(), Error> {
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
    let mut current_encoding = None;
    for operation in &mut content.operations {
        match operation.operator.as_ref() {
            "Tf" => {
                let current_font = operation
                    .operands
                    .get(0)
                    .ok_or_else(|| Error::Syntax("missing font operand".to_string()))?
                    .as_name()?;
                current_encoding = encodings.get(current_font).map(std::string::String::as_str);
            }
            "Tj" | "TJ" => {
                //let mut _collect_text_string = String::new();
                //collect_text(&mut _collect_text_string, current_encoding, &operation.operands);
                //info!("::->{}", _collect_text_string);
                for bytes in operation.operands.iter_mut().flat_map(Object::as_str_mut) {
                    let decoded_text = Document::decode_text(current_encoding, bytes);
                    if decoded_text.contains(text) {
                        info!("{}", decoded_text);
                        let new_text = decoded_text.replace(text, other_text);
                        let encoded_bytes = Document::encode_text(current_encoding, &new_text);
                        *bytes = encoded_bytes;
                    }
                }
                for arrs in operation.operands.iter_mut().flat_map(Object::as_array_mut) {
                    for bytes in arrs.iter_mut().flat_map(Object::as_str_mut) {
                        let decoded_text = Document::decode_text(current_encoding, bytes);
                        if decoded_text.contains(text) {
                            info!("...->{}", decoded_text);
                            let new_text = decoded_text.replace(text, other_text);
                            let encoded_bytes = Document::encode_text(current_encoding, &new_text);
                            *bytes = encoded_bytes;
                        }
                    }
                }
            }
            _ => {}
        }
    }
    let modified_content = content.encode()?;
    doc.change_page_content(page_id, modified_content)
}

fn main() -> Result<(), Error> {

    env_logger::init();

    let mut doc = Document::load("example.pdf").unwrap();

    doc.version = "1.4".to_string();
    replace_text(&mut doc, 1, "SDI", "DDD")?;
    // Store file in current working directory.
    // Note: Line is excluded when running tests
    if true {
        doc.save("modified.pdf").unwrap();
    }
    Ok(())
}
