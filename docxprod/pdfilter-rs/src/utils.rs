use scraper::{Html, Selector};

pub fn parse_text_style(attr: &str) -> (String, String, bool) {
    let style: Vec<_> = attr
        .split(";")
        .map(|x| {
            let mut m = std::collections::HashMap::new();
            let y: Vec<&str> = x.split(":").collect();
            if y.len() > 1 {
                m.insert(y[0], y[1]);
            } else {
                m.insert(y[0], "");
            }
            m
        })
        .collect();
    let mut text_color = "".to_string();
    let mut text_align = "".to_string();
    let mut text_bold = false;
    for style_field in style {
        if style_field.contains_key("text-align") {
            text_align = style_field.get("text-align").unwrap().to_string();
        } else if style_field.contains_key("font-weight") {
            text_bold = style_field
                .get("font-weight")
                .unwrap()
                .eq_ignore_ascii_case("bold");
        } else if style_field.contains_key("color") {
            text_color = style_field.get("color").unwrap().to_string();
        }
    }
    return (text_color, text_align, text_bold);
}

#[allow(dead_code)]
pub fn parse_text_attr_style(html: &str) -> (String, String, bool) {
    let fragment = Html::parse_fragment(html);
    let selector = Selector::parse("div").unwrap();
    let div = fragment.select(&selector).next().unwrap();
    let div_style = div.value().attr("style").unwrap();

    return parse_text_style(div_style);
}

#[cfg(test)]
mod tests {
    use crate::utils::parse_text_attr_style;

    #[test]
    fn test_parse_text_attr_style() {
        let html = r#"<div style="color:red;text-align:center;font-weight:bold">"#;
        let (text_color, text_align, text_bold) = parse_text_attr_style(html);
        assert_eq!("center", text_align);
        assert_eq!(true, text_bold);
        assert_eq!("red", text_color);
    }
}
