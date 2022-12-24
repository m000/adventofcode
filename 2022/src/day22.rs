use clap::Parser;
use env_logger::Env;
use log::{debug, info};
use std::cmp::{max, min};
use std::fs::File;
use std::io::{BufRead, BufReader};
use utf8_read::Reader;

/// Advent of Code 2022, Day 16
#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Args {
    /// Input file to read
    input: String,

    /// Part of the puzzle to solve
    #[arg(short, long, value_parser = clap::value_parser!(u32).range(1..=2))]
    part: u32,
}

#[derive(Debug)]
struct Move {
    steps: Option<usize>,
    rotate: Option<char>,
}

#[derive(Debug)]
struct Position {
    y: usize,
    x: usize,
    face: char,
}

type Map = Vec<String>;

/// Read input file, yielding a map, the list of moves and the initial position.
fn read_input(reader: &mut BufReader<File>) -> (Map, Vec<Move>, Position) {
    // Read and normalize map.
    let mut map_width = 0;
    let mut map = reader
        .lines()
        .map(|line| line.unwrap())
        .take_while(|line| line.trim().len() > 0)
        .filter(|line| {
            map_width = max(map_width, line.len());
            true
        })
        .collect::<Map>() // collect so that map_width is final
        .iter()
        .map(|line| String::from("x") + &line.replace(" ", "x") + &"x".repeat(map_width - line.len() + 1)) // normalize based on map_width
        .collect::<Map>();

    // Find start position.
    let start = map[0].find(|c| c != 'x').unwrap();

    // Add border rows to make bound checks easier.
    map.insert(0, "x".repeat(map_width + 2));
    map.push("x".repeat(map_width + 2));

    // Read moves.
    let moves = Reader::new(reader)
        .into_iter()
        .map(|c| c.unwrap())
        .filter(|c| c.is_ascii_digit() || c == &'L' || c == &'R') // filter out any garbage
        .collect::<String>();
    let moves = moves
        .split_inclusive(|c| c == 'L' || c == 'R')
        .map(|s| {
            match s.chars().last().unwrap() {
                rotate @ ('L' | 'R') => Move {
                    steps: Some(s[..s.len() - 1].parse::<usize>().unwrap()),
                    rotate: Some(rotate),
                },
                _ => Move {
                    // covers last move, where there may be no rotation part
                    steps: Some(s.parse::<usize>().unwrap()),
                    rotate: None,
                },
            }
        })
        .collect::<Vec<Move>>();

    return (
        map,
        moves,
        Position {
            y: 1,
            x: start,
            face: 'E',
        },
    );
}

fn cube_scan(map: &Map, pos: &Position) {
    // Identify the cube side length as the minimum number of non-void ('x') cells in a row.
    let cube_side = map
        .iter()
        .map(|row| row.chars().filter(|c| c != &'x').count())
        .filter(|len| len > &0)
        .min()
        .unwrap();

    info!("{cube_side:?}");
}

/// Take a step forward and return the new position.
fn step(map: &Map, mv: &Move, pos: &mut Position) {
    // Move forward.
    info!("{pos:?} {mv:?}");
    for steps_taken in 1..=mv.steps.expect("Move with no steps encountered.") {
        let orig = Position {
            y: pos.y,
            x: pos.x,
            face: pos.face,
        };

        // One step forward.
        match pos.face {
            'E' => pos.x += 1,
            'W' => pos.x = (pos.x as u32 - 1) as usize,
            'S' => pos.y += 1,
            'N' => pos.y = (pos.y as u32 - 1) as usize,
            _ => {
                panic!("Position facing an unknown direction: {pos:?}")
            }
        }

        // Check what we find in the new position.
        // Because of the border rows/columns we have added to input, we will always find something.
        // Repeat until we land on an empty space ('.') to handle teleportations.
        let mut stop = false;
        while match map[pos.y].chars().nth(pos.x) {
            Some('.') => {
                /* empty space - break loop */
                false
            }
            Some('#') => {
                /* wall - step back and break loop */
                debug!("Hit wall after {steps_taken} steps.");
                pos.y = orig.y;
                pos.x = orig.x;
                stop = true; // break outer loop
                false
            }
            Some('x') => {
                /* wrap teleport - go to the other side and try again */
                debug!("Teleporting!");
                match pos.face {
                    'E' => {
                        pos.x = map[pos.y].find(|c| c != 'x').unwrap();
                    }
                    'W' => {
                        pos.x = map[pos.y].rfind(|c| c != 'x').unwrap();
                    }
                    'S' => {
                        let col = map
                            .iter()
                            .map(|row| row.chars().nth(pos.x).unwrap())
                            .collect::<String>();
                        pos.y = col.find(|c| c != 'x').unwrap();
                    }
                    'N' => {
                        let col = map
                            .iter()
                            .map(|row| row.chars().nth(pos.x).unwrap())
                            .collect::<String>();
                        pos.y = col.rfind(|c| c != 'x').unwrap();
                    }
                    _ => {
                        panic!("Position facing an unknown direction: {pos:?}")
                    }
                }
                true
            }
            map_cell @ _ => {
                panic!("Unknown cell type at {pos:?}: {map_cell:?}");
            }
        } {}

        debug!("{pos:?}");
        if stop {
            break;
        }
    }

    // Rotate.
    pos.face = match (mv.rotate, pos.face) {
        (Some('L'), 'E') => 'N',
        (Some('L'), 'W') => 'S',
        (Some('L'), 'S') => 'E',
        (Some('L'), 'N') => 'W',
        (Some('R'), 'E') => 'S',
        (Some('R'), 'W') => 'N',
        (Some('R'), 'S') => 'W',
        (Some('R'), 'N') => 'E',
        (None, _) => pos.face,
        _ => {
            panic!(
                "Do not know how to rotate for {:?} while facing {:?}.",
                mv.rotate, pos.face
            )
        }
    };
}

fn main() {
    env_logger::Builder::from_env(Env::default().default_filter_or("info"))
        .format_timestamp(None)
        .init();
    let args = Args::parse();

    let filename = &args.input;
    let (map, moves, mut pos) = read_input(&mut BufReader::new(File::open(filename).unwrap_or_else(|err| {
        panic!("Error opening {filename}: {err:?}");
    })));

    cube_scan(&map, &pos);
    return;

    moves.iter().for_each(|m| {
        step(&map, &m, &mut pos);
    });

    let face_value = "ESWN";
    info!(
        "Password: {}",
        1000 * pos.y + 4 * pos.x + face_value.find(pos.face).unwrap()
    );
}
