use std::{error::Error, io, fs};

#[derive(Debug, serde::Deserialize)]
#[allow(non_snake_case, dead_code)]
struct Record {
    Section_Dataset_Id: String,
    Gene: String,
    Images: String,
}

#[allow(dead_code)]
fn get_all_image_ids() -> Result<(), Box<dyn Error>> {
    let mut rdr = csv::Reader::from_reader(io::stdin());
    for result in rdr.deserialize() {
        // Notice that we need to provide a type hint for automatic
        // deserialization.
        let record: Record = result?;
        //Converts the list of Images_ids from a string to a list of integers 
        let images: &Vec<u32> = &record.Images[1..record.Images.len()-1].split(",").map(|x| x.parse::<u32>().unwrap()).collect();
        println!("{:?}\n", images);
    }
    Ok(())
}


fn get_directories () {
    let paths = fs::read_dir("../../Datasets/Outputs/Chunked").unwrap();
    let mut count = 0;
    for path in paths {
        println!("{}", path.unwrap().path().display());
        count+=1;
    }

    println!("{count}");

}


fn main() {
    /* 
    if let Err(err) = get_all_image_ids() {
        println!("error running example: {}", err);
        process::exit(1);
    }
    */
    get_directories();
}