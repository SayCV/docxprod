use color_name;
use colors_transform::{Hsl, Rgb, Color};
use scraper::{Html, Selector};

#[allow(dead_code)]
pub fn to_docx_color(text_color: &str) -> String {
    let mut hex_color= text_color.parse::<Rgb>().ok();
    if hex_color.is_none() {
        hex_color= Rgb::from_hex_str(text_color).ok();
    }
    if hex_color.is_none() {
        let hsl_color= text_color.parse::<Hsl>().ok();
        if hsl_color.is_some() {
            hex_color = Some(hsl_color.unwrap().to_rgb());
        }
    }
    if hex_color.is_none() {
        let _color= color_name::Color::val().by_string(text_color.to_string());
        if _color.is_ok() {
            let rgb = _color.ok().unwrap();
            hex_color = Some(Rgb::from_tuple(&(rgb[0] as f32, rgb[1] as f32, rgb[2] as f32)));
        }
    }
    if hex_color.is_some() {
        return hex_color.unwrap().to_css_hex_string().strip_prefix("#").unwrap().to_string();
    }
    return "".to_string();
}

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
    use color_name::Color;

    use crate::utils::{parse_text_style, parse_text_attr_style, to_docx_color};

    #[test]
    fn test_parse_text_attr_style() {
        let html = r#"<div style="color:red;text-align:center;font-weight:bold">"#;
        let (text_color, text_align, text_bold) = parse_text_attr_style(html);
        assert_eq!("red", text_color);
        assert_eq!("center", text_align);
        assert_eq!(true, text_bold);
    }

    #[test]
    fn test_parse_text_color() {
        let html = r#"color:red;text-align:center;font-weight:bold"#;
        let (text_color, _, _) = parse_text_style(html);
        assert_eq!("red", text_color);
        assert_eq!("ff0000", to_docx_color(&text_color));
    }

    #[test]
    fn test_color_by_string_fn() {
        assert_eq!(
            Color::val()
                .by_string(String::from("red"))
                .expect("Not Found"),
            [255, 0, 0]
        );
    }
}
