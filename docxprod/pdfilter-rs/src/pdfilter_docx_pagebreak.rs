extern crate pandoc_ast;

#[allow(unused_imports)]
use pandoc_ast::{Attr, Block, Format, Inline, MutVisitor};
use std::io::{self, Read, Write};

use lazy_static::lazy_static;
use regex::Regex;

struct MyVisitor;

static PAGEBREAK: &str = r#"<w:p><w:r><w:br w:type="page" /></w:r></w:p>"#;
static mut OCCURS: i32 = 0;

impl MutVisitor for MyVisitor {
    fn visit_block(&mut self, block: &mut Block) {
        use Block::*;
        match *block {
            Div(ref attr, _) => {
                for extra_attr in &attr.2 {
                    if extra_attr.0.eq_ignore_ascii_case("style") {
                        lazy_static! {
                            static ref RE_PAGE_BREAK: Regex =
                                Regex::new(r"page-break-after\s+:\s+always;").unwrap();
                        }
                        if RE_PAGE_BREAK.is_match(&extra_attr.1.to_lowercase()) {
                            *block = Block::RawBlock(Format("openxml".to_string()), PAGEBREAK.to_string());
                            unsafe { OCCURS+=1 };
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
    let mut s = String::new();
    io::stdin().read_to_string(&mut s).unwrap();
    let s = pandoc_ast::filter(s, |mut pandoc| {
        MyVisitor.walk_pandoc(&mut pandoc);
        pandoc
    });
    unsafe { if OCCURS >0 { eprintln!("-> Processed page break at {} positions.", OCCURS); } }
    io::stdout().write(s.as_bytes()).unwrap();
}
