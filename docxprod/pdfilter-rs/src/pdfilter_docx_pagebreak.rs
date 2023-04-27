extern crate pandoc_ast;

#[allow(unused_imports)]
use pandoc_ast::{Attr, Block, Format, Inline, MutVisitor};
use std::io::{self, Read, Write};

use lazy_static::lazy_static;
use regex::Regex;

struct MyVisitor {
    processed_count: i32,
}

static PAGEBREAK: &str = r#"<w:p><w:r><w:br w:type="page" /></w:r></w:p>"#;

impl MutVisitor for MyVisitor {
    fn visit_block(&mut self, block: &mut Block) {
        use Block::*;
        match *block {
            Div(ref attr, _) => {
                for extra_attr in &attr.2 {
                    if extra_attr.0.eq_ignore_ascii_case("style") {
                        lazy_static! {
                            static ref RE_PAGE_BREAK: Regex =
                                Regex::new(r".*page-break-after\s*:\s*always\s*;.*").unwrap();
                        }
                        if RE_PAGE_BREAK.is_match(&extra_attr.1.to_lowercase()) {
                            *block = Block::RawBlock(
                                Format("openxml".to_string()),
                                PAGEBREAK.to_string(),
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
