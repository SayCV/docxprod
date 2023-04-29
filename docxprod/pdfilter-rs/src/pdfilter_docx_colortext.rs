pub mod utils;

extern crate pandoc_ast;

#[allow(unused_imports)]
use pandoc_ast::{Attr, Block, Format, Inline, MutVisitor};
use std::io::{self, Read, Write};

use crate::utils::to_docx_color;

struct MyVisitor {
    processed_count: i32,
}

fn colored_text(text: &str, color_hex: &str, bold: bool) -> String {
    format!(
        "{}{}{}{}{}{}",
        r#"<w:r><w:rPr><w:color w:val=""#,
        color_hex,
        r#"" /></w:rPr><w:t>"#,
        if bold {
            r#"<w:rPr><w:b /></w:rPr>"#
        } else {
            ""
        },
        text,
        r#"</w:t></w:r>"#
    )
}

impl MutVisitor for MyVisitor {
    fn visit_inline(&mut self, inline: &mut Inline) {
        use Inline::*;
        match inline.clone() {
            Span(ref mut attr, vec_inline) => {
                for extra_attr in &attr.2 {
                    if extra_attr.0.eq_ignore_ascii_case("style") {
                        let (text_color, _, text_bold) = utils::parse_text_style(&extra_attr.1);
                        if !text_color.is_empty() {
                            let hex_color = to_docx_color(&text_color);
                            let mut text = String::new();
                            let mut elem = String::new();
                            for _inline in vec_inline {
                                match _inline {
                                    Inline::Str(ref s) => text.push_str(s),
                                    Inline::Space | Inline::SoftBreak => text.push_str(" "),
                                    Inline::LineBreak => {
                                        elem.push_str(&colored_text(&text, &hex_color, text_bold));
                                        elem.push_str(r"<w:r><w:br /></w:r>");
                                        text.clear();
                                    }
                                    _ => {}
                                }
                            }
                            if text.len() > 0 {
                                elem.push_str(&colored_text(&text, &hex_color, text_bold));
                            }
                            *inline = Inline::RawInline(
                                Format("openxml".to_string()),
                                elem,
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
            eprintln!("-> Processed at {} positions.", my_visitor.processed_count);
        }
        io::stdout().write(s.as_bytes()).unwrap();
    } else {
        io::stdout().write(s.as_bytes()).unwrap();
    }
}
