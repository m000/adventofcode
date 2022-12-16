use clap::Parser;
use env_logger::Env;
use log::{debug, info};
use std::collections::{HashMap, HashSet};
use std::fs::File;
use std::io::{BufRead, BufReader};
//use z3::{ast, Config, Context, Optimize, SatResult, Solver};

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
struct CaveRoom {
    name: String,
    flow_rate: u32,
    neighbors: HashSet<String>,
    distance: HashMap<String, u32>,
}

fn room_dist<'a>(
    r1: &'a String,
    r2: &'a String,
    all: &'a HashMap<String, CaveRoom>,
    visited: &mut Vec<&'a String>,
) -> Option<u32> {
    let room1 = all.get(r1).unwrap();
    let room2 = all.get(r2).unwrap();
    let (dist, method) = match (room1.neighbors.contains(r2), room2.distance.contains_key(r1)) {
        (true, _) => (Some(1), "trivial"),
        (false, true) => (Some(room2.distance[r1]), "precomputed"),
        (false, false) => {
            // recurse
            match visited.contains(&r1) {
                false => {
                    // not computed
                    match room1
                        .neighbors
                        .iter()
                        .map(|n| {
                            visited.push(r1);
                            let dist = room_dist(n, r2, all, visited);
                            visited.pop();
                            dist
                        })
                        .min()
                    {
                        Some(dist) => (Some(dist + 1), "recursed"),
                        _ => (None, "dead end"),
                    }
                }
                true => {
                    // cycle - unreachable
                    (None, "loop")
                }
            }
        }
    };
    debug!("walked:{visited:?} next:{r1:?} dest:{r2:?} -> {dist:?} ({method})");
    dist
}

fn read_rooms(reader: &mut BufReader<File>) -> HashMap<String, CaveRoom> {
    // Read room information.
    let mut rooms = reader
        .lines()
        .enumerate()
        .map(|(lineno, line)| {
            let lineno_1 = lineno + 1;
            (
                lineno_1,
                line.unwrap_or_else(|err| {
                    panic!("{err:?}: {lineno_1}");
                }),
            )
        })
        .map(|(lineno_1, line)| {
            // Format:
            // Valve <VALVE> has flow rate=<RATE>; tunnels lead to valves <N1>, <N2>...
            //   0      1     2    3      4           5      6   7    8
            let tokens = line.split_whitespace().collect::<Vec<_>>();
            let room = CaveRoom {
                name: tokens[1].to_string(),
                flow_rate: {
                    let mut s = tokens[4].to_string();
                    s.retain(|c| c.is_ascii_digit());
                    s.parse::<u32>().unwrap_or_else(|err| {
                        panic!("Error parsing flow rate at line {lineno_1}: {err:?}");
                    })
                },
                neighbors: tokens[9..]
                    .iter()
                    .map(|s| {
                        let mut s = s.to_string();
                        s.retain(|c| c.is_ascii_uppercase());
                        s
                    })
                    .collect::<HashSet<_>>(),
                distance: HashMap::<_, _>::new(),
            };
            debug!("Line {lineno_1:03}: {room:?}");
            (room.name.clone(), room)
        })
        .collect::<HashMap<_, _>>();
    return rooms;
}

fn main() {
    env_logger::Builder::from_env(Env::default().default_filter_or("info"))
        .format_timestamp(None)
        .init();
    let args = Args::parse();

    let filename = &args.input;
    let rooms = read_rooms(&mut BufReader::new(File::open(filename).unwrap_or_else(|err| {
        panic!("Error opening {filename}: {err:?}");
    })));

    info!(
        "{:?}",
        room_dist(
            &"AA".to_string(),
            &"HH".to_string(),
            &rooms,
            &mut Vec::<&String>::new()
        )
    );

    /*
    let cfg = Config::new();
    let ctx = Context::new(&cfg);
    //let opt = Optimize::new(&ctx);
    let slv = Solver::new(&ctx);

    let i_1 = &ast::Int::from_u64(&ctx, 4);
    let i_2 = &ast::Int::from_u64(&ctx, 10);
    let foo = ast::Int::new_const(&ctx, "x");
    slv.assert(&foo.gt(i_1));
    info!("{i_1:?}");
    let mut x = &ast::Int::from_u64(&ctx, 4);
    assert_eq!(slv.check(), SatResult::Sat);

    let model = slv.get_model().unwrap();
    info!("{:?}", model.eval(&foo, true).unwrap().as_i64().unwrap());
    */

    //34         .take_while(|(_lineno_1, line)| line.trim().len() > 0)
    //35         .map(|(_lineno_1, line)| line)
    //36         .collect::<Vec<_>>();
    /*
    let marker_size: usize = match args.part {
        1 => 4,
        2 => 14,
        part @ _ => panic!("Don't know how to run part {part}."),
    };
    let mut buf = CircularBuffer::<char>::new(marker_size);
    */

    /*
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
    */
    debug!("");
}
