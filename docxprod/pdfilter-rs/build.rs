use std::env;
use fs_extra::copy_items;
use fs_extra::dir::CopyOptions;
use std::path::Path;
use anyhow::*;

static DATA_DIR: &str = "../data";
static CONFIG_DIR: &str = "../config";

pub fn copy_to_output(path: &str, build_type: &str) -> Result<()> {
    let mut options = CopyOptions::new();
    let mut from_path = Vec::new();
    let out_path = format!("target/{}", build_type);

    // Overwrite existing files with same name
    options.overwrite = true;

    from_path.push(path);
    copy_items(&from_path, &out_path, &options)?;

    Ok(())
}

pub fn copy_to_output_path(path: &Path, build_type: &str) -> Result<()> {
    let path_str = path.to_str().expect("Could not convert file path to string");
    copy_to_output(path_str, build_type)?;

    Ok(())
}

pub fn copy_to_install_bin(path: &str, folder: &str) -> Result<()> {
    let mut options = CopyOptions::new();
    let mut from_path = Vec::new();
    let cargo_home = env::var("CARGO_HOME").unwrap();
    let out_path_string = format!("{}/{}", cargo_home, folder);
    let out_path = Path::new(&out_path_string);
    if !out_path.exists() {
        fs_extra::dir::create_all(out_path, false)?;
    }

    // Overwrite existing files with same name
    options.overwrite = true;

    from_path.push(path);
    copy_items(&from_path, &out_path, &options)?;

    Ok(())
}

pub fn copy_to_install_bin_path(path: &Path, folder: &str) -> Result<()> {
    let path_str = path.to_str().expect("Could not convert file path to string");
    copy_to_install_bin(path_str, folder)?;

    Ok(())
}

fn main() {
    // Re-runs the script if any files in res are changed
    println!("cargo:rerun-if-changed={}/*", DATA_DIR);
    //copy_to_output_path(Path::new(DATA_DIR), &env::var("PROFILE").unwrap()).expect("Could not copy");
    copy_to_install_bin_path(Path::new(DATA_DIR), "bin/dcoxprod").expect("Could not copy");

    println!("cargo:rerun-if-changed={}/*", CONFIG_DIR);
    copy_to_install_bin_path(Path::new(CONFIG_DIR), "bin/dcoxprod").expect("Could not copy");
}
