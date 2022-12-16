use clap::Parser;
use env_logger::Env;
use log::{debug, info};
use rbl_circular_buffer::CircularBuffer;
use std::collections::HashSet;
use std::fs::File;
use std::io::BufReader;
use utf8_read::Reader;

/// Advent of Code 2022, Day 6
#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Args {
    /// Input file to read
    input: String,

    /// Part of the puzzle to solve
    #[arg(short, long, value_parser = clap::value_parser!(u32).range(1..=2))]
    part: u32,
}

fn main() {
    env_logger::Builder::from_env(Env::default().default_filter_or("info"))
        .format_timestamp(None)
        .init();
    let args = Args::parse();

    let marker_size: usize = match args.part {
        1 => 4,
        2 => 14,
        part @ _ => panic!("Don't know how to run part {part}."),
    };
    let filename = &args.input;
    let mut reader = Reader::new(BufReader::new(File::open(filename).unwrap_or_else(|err| {
        panic!("Error opening {filename}: {err:?}");
    })));
    let mut buf = CircularBuffer::<char>::new(marker_size);

    let first_marker_position = reader
        .into_iter()
        .enumerate()
        .map(|(i, x)| x.unwrap_or_else(|err| panic!("Error reading {filename}:C{i}: {err:?}")))
        .filter(|x| x != &'\n') // exclude any newlines
        .enumerate() // renumber
        .position(|(i, c)| {
            buf.push(c); // update circular buffer
            let unique = HashSet::<char>::from_iter(buf);
            debug!("Position {i:04}: c={c:?}, buf={buf}, unique={}", unique.len());
            unique.len() == marker_size
        })
        .expect("No marker found in input!")
        + 1;

    info!("First marker of size {marker_size} at position {first_marker_position}.");
}
