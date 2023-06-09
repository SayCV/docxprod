extern crate pandoc_ast;

#[allow(unused_imports)]
use pandoc_ast::{Attr, Block, Format, Inline, MutVisitor};

use std::io::{self, Read, Write};

mod utils;

struct MyVisitor {
    processed_count: i32,
}

fn centered_text(text: &str, bold: bool) -> String {
    format!(
        "{}{}{}{}",
        r#"<w:p><w:pPr><w:pStyle w:val="FirstParagraph" /><w:jc w:val="center" /></w:pPr><w:r><w:t>"#,
        if bold { r#"<w:rPr><w:b /></w:rPr>"# } else { "" },
        text,
        r#"</w:t></w:r></w:p>"#
    )
}

impl MutVisitor for MyVisitor {
    fn visit_block(&mut self, block: &mut Block) {
        use Block::*;
        match block.clone() {
            Div(ref mut attr, vec_block) => {
                for extra_attr in &attr.2 {
                    if extra_attr.0.eq_ignore_ascii_case("style") {
                        let (_, text_align, text_bold) = utils::parse_text_style(&extra_attr.1);
                        if text_align.eq_ignore_ascii_case("center") {
                            let mut text = String::new();
                            for _block in vec_block {
                                match _block {
                                    Plain(ref vec_inline) | Para(ref vec_inline) => {
                                        for inline in vec_inline {
                                            match inline {
                                                Inline::Str(ref s) => text.push_str(s),
                                                _ => {},
                                            };
                                        }
                                    }
                                    _ => {}
                                }
                            }
                            *block = Block::RawBlock(
                                Format("openxml".to_string()),
                                centered_text(&text, text_bold).to_string(),
                            );
                            self.processed_count += 1;
                            break;
                        }
                    }
                }
            }
            _ => {}
        }
    }
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let format = match args.len() {
        _ if args.len() > 1  => args[1].clone(),
        _ => "html".to_string(),
    };
    //eprintln!("-> Detected format {}.", format);

    let mut s = String::new();
    let mut my_visitor = MyVisitor { processed_count: 0 };
    io::stdin().read_to_string(&mut s).unwrap();
    if format.eq_ignore_ascii_case("docx") {
        let s = pandoc_ast::filter(s, |mut pandoc| {
            my_visitor.walk_pandoc(&mut pandoc);
            pandoc
        });
        if my_visitor.processed_count > 0 {
            eprintln!(
                "-> Processed at {} positions.",
                my_visitor.processed_count
            );
        }
        io::stdout().write(s.as_bytes()).unwrap();
    } else {
        io::stdout().write(s.as_bytes()).unwrap();
    }
}
