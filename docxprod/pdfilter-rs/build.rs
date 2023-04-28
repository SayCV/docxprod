use std::env;
use fs_extra::copy_items;
use fs_extra::dir::CopyOptions;
use std::path::Path;
use anyhow::*;

static DATA_DIR: &str = "../data";
static CONFIG_DIR: &str = "../config";

pub fn copy_to_install_bin(path: &str, folder: &str) -> Result<()> {
    let mut options = CopyOptions::new();
    let mut from_path = Vec::new();
    let out_path = Path::new(folder);
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
    let cargo_home = env::var("CARGO_HOME").unwrap();
    let out_path = format!("{}/{}", cargo_home, "bin/dcoxprod");
    // Re-runs the script if any files in res are changed
    println!("cargo:rerun-if-changed={}/*", DATA_DIR);
    //copy_to_output_path(Path::new(DATA_DIR), &env::var("PROFILE").unwrap()).expect("Could not copy");
    copy_to_install_bin_path(Path::new(DATA_DIR), &out_path).expect("Could not copy");

    println!("cargo:rerun-if-changed={}/*", CONFIG_DIR);
    copy_to_install_bin_path(Path::new(CONFIG_DIR), &out_path).expect("Could not copy");
}
