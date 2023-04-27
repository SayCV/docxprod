extern crate pandoc_ast;

#[allow(unused_imports)]
use pandoc_ast::{Attr, Block, Format, Inline, MutVisitor};
use std::io::{self, Read, Write};

use lazy_static::lazy_static;
use regex::Regex;

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
            Div(ref attr, vec_block) => {
                for extra_attr in &attr.2 {
                    if extra_attr.0.eq_ignore_ascii_case("style") {
                        lazy_static! {
                            static ref RE_TEXT_ALIGN_CENTER: Regex =
                                Regex::new(r".*text-align\s*:\s*center\s*.*").unwrap();
                            static ref RE_TEXT_BOLD: Regex =
                                Regex::new(r".*font-weight\s*:\s*bold\s*.*").unwrap();
                        }
                        if RE_TEXT_ALIGN_CENTER.is_match(&extra_attr.1.to_lowercase()) {
                            let mut text = String::new();
                            for _block in vec_block.clone() {
                                match _block {
                                    Plain(ref vec_inline) | Para(ref vec_inline) => {
                                        for inline in vec_inline {
                                            match inline {
                                                Inline::Str(ref s) => text.push_str(s),
                                                _ => text.push_str(""),
                                            };
                                        }
                                    }
                                    _ => {}
                                }
                            }
                            let bold = RE_TEXT_BOLD.is_match(&extra_attr.1.to_lowercase());
                            *block = Block::RawBlock(
                                Format("openxml".to_string()),
                                centered_text(&text, bold).to_string(),
                            );
                            self.processed_count += 1;

                            //let attr0 = &attr.0;
                            //let attr1 = attr.1.iter().map(|x| x.as_str()).collect::<String>();
                            //let attr2 = attr.2.iter().map(|x| x.0.to_string() + " = " + &x.1.to_string() ).collect::<String>();
                            //eprintln!("-> {} -> {} -> {} -> {}", attr0, attr1, attr2, text);
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
    let mut format = "html".to_string();
    if args.len() > 1 {
        format = args[1].clone();
    }
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
