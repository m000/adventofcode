#![feature(drain_filter)]
use clap::Parser;
use env_logger::Env;
use log::{debug, info};
use std::cell::Cell;
use std::fmt;
use std::fs::File;
use std::io::{BufRead, BufReader};

/// Advent of Code 2022, Day 24
#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Args {
    /// Input file to read
    input: String,

    /// Part of the puzzle to solve
    #[arg(short, long, value_parser = clap::value_parser!(u32).range(1..=2))]
    part: u32,
}

type MapGrid = Vec<Vec<MapPos>>;
type Position = (usize, usize);

struct MapPos {
    blizzards: Vec<char>,
    wall: bool,
}

struct Map {
    grid: MapGrid,
    start: Position,
    exit: Position,
    player: Cell<Position>, // only used for rendering
}

impl MapPos {
    /// Convert a MapPosition to a char, for display purposes.
    pub fn to_char(&self) -> char {
        let nblizzards = self.blizzards.len();
        match (self, nblizzards) {
            (MapPos { wall: true, .. }, _) => '#',
            (MapPos { wall: false, .. }, 0) => '.',
            (MapPos { wall: false, .. }, 1) => self.blizzards[0],
            (MapPos { wall: false, .. }, 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9) => {
                char::from_digit(nblizzards as u32, 10).unwrap()
            }
            _ => 'X',
        }
    }
}

impl Map {
    /// Create a new empty Map with the specified dimensions.
    pub fn empty((nrows, ncols): (usize, usize)) -> Map {
        let start = (1, 0);
        let exit = (ncols - 2, nrows - 1);

        Map {
            grid: (0..nrows)
                .map(|nrow| {
                    (0..ncols)
                        .map(|ncol| MapPos {
                            blizzards: Vec::new(),
                            wall: match (ncol, nrow) {
                                (ncol, nrow) if (ncol, nrow) == start => false,
                                (ncol, nrow) if (ncol, nrow) == exit => false,
                                (ncol, _) if (ncol == 0 || ncol == ncols - 1) => true,
                                (_, nrow) if (nrow == 0 || nrow == nrows - 1) => true,
                                _ => false,
                            },
                        })
                        .collect::<Vec<MapPos>>()
                })
                .collect::<MapGrid>(),
            start: start,
            exit: exit,
            player: Cell::new(start),
        }
    }

    /// Create a new empty map with the same dimensions and position as the reference map.
    pub fn empty_from(map: &Map) -> Map {
        let mut new_map = Map::empty((map.grid.len(), map.grid[0].len()));
        new_map.start = map.start;
        new_map.exit = map.exit;
        new_map
    }

    /// Read a map from a file.
    pub fn from_file(filename: &str) -> Map {
        let grid = BufReader::new(File::open(filename).unwrap_or_else(|err| {
            panic!("Error opening {filename}: {err:?}");
        }))
        .lines()
        .map(|line| {
            line.unwrap()
                .chars()
                .map(|c| match c.clone() {
                    '#' => MapPos {
                        blizzards: Vec::new(),
                        wall: true,
                    },
                    '.' => MapPos {
                        blizzards: Vec::new(),
                        wall: false,
                    },
                    '>' | '<' | '^' | 'v' => MapPos {
                        blizzards: Vec::from([c]),
                        wall: false,
                    },
                    _ => panic!("Unknown character encountered while reading map: {c:?}"),
                })
                .collect::<Vec<MapPos>>()
        })
        .collect::<MapGrid>();

        let start = (1, 0);
        let exit = (grid[0].len() - 2, grid.len() - 1);
        Map {
            grid: grid,
            start: start,
            exit: exit,
            player: Cell::new(start),
        }
    }

    /// Calculates the next blizzard position on the map.
    pub fn next_blizzard_pos(&self, colnum: usize, rownum: usize, b: char) -> (usize, usize) {
        let (mut colnum_next, mut rownum_next) = (colnum, rownum);
        match b {
            '>' => {
                colnum_next += 1;
                if self.grid[rownum_next][colnum_next].wall {
                    colnum_next = 1;
                }
            }
            '<' => {
                colnum_next -= 1;
                if self.grid[rownum_next][colnum_next].wall {
                    colnum_next = self.grid[0].len() - 2;
                }
            }
            '^' => {
                rownum_next -= 1;
                if self.grid[rownum_next][colnum_next].wall {
                    rownum_next = self.grid.len() - 2;
                }
            }
            'v' => {
                rownum_next += 1;
                if self.grid[rownum_next][colnum_next].wall {
                    rownum_next = 1;
                }
            }
            _ => panic!("Unknown blizzard type encountered in ({colnum}, {rownum}): {b:?}"),
        }
        (colnum_next, rownum_next)
    }

    /// Returns the map with the positions of the blizzards on the next minute.
    pub fn next_minute(&self) -> Map {
        let mut new_map = Map::empty_from(self);

        // Populate empty map with blizzards.
        self.grid.iter().enumerate().for_each(|(rownum, row)| {
            row.iter()
                .enumerate()
                .filter(|(_colnum, pos)| pos.wall == false && pos.blizzards.len() > 0)
                .for_each(|(colnum, pos)| {
                    pos.blizzards.iter().for_each(|b| {
                        let (colnum_next, rownum_next) = self.next_blizzard_pos(colnum, rownum, *b);
                        new_map.grid[rownum_next][colnum_next].blizzards.push(*b);
                    })
                })
        });

        new_map
    }

    /// Returns the available positions to move on the map.
    pub fn available_moves(&self, start: &Position) -> Vec<Position> {
        self.grid
            .iter()
            .enumerate()
            .filter(|(rownum, _row)| {
                let rowdist = (*rownum as i32 - start.1 as i32).abs();
                rowdist <= 1 // keep adjacent and curent rows
            })
            .map(|(rownum, row)| {
                let rowdist = (rownum as i32 - start.1 as i32).abs();
                row.iter()
                    .enumerate()
                    .filter(|(colnum, pos)| {
                        let coldist = (*colnum as i32 - start.0 as i32).abs();

                        coldist <= 1 // keep adjacent and current columns
                        && coldist + rowdist <= 1 // exclude diagonal neighbors
                        && !pos.wall // exclude walls
                        && pos.blizzards.len() == 0 // exclude positions with blizzards
                    })
                    .map(|(colnum, _pos)| (colnum, rownum))
                    .collect::<Vec<Position>>()
            })
            .flatten()
            .collect::<Vec<Position>>()
    }
}

impl fmt::Display for Map {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f,
            "\n{}",
            self.grid
                .iter()
                .enumerate()
                .map(|(rownum, row)| format!(
                    "{}\n",
                    row.iter()
                        .enumerate()
                        .map(|(colnum, pos)| {
                            let c = pos.to_char();
                            match (colnum, rownum) {
                                (colnum, rownum) if self.player.get() == (colnum, rownum) && c == '.' => '■', // current position
                                (colnum, rownum) if self.player.get() == (colnum, rownum) && c != '.' => 'E', // indicate error
                                (colnum, rownum) if self.exit == (colnum, rownum) && c == '.' => '✕', // exit
                                _ => c,
                            }
                        })
                        .collect::<String>()
                ))
                .collect::<String>()
                .trim_end()
        )
    }
}

fn main() {
    env_logger::Builder::from_env(Env::default().default_filter_or("info"))
        .format_timestamp(None)
        .init();
    let args = Args::parse();

    let nways: usize = match args.part {
        1 => 1, // start-exit
        2 => 3, // start-exit-start-exit
        part @ _ => panic!("Don't know how to run part {part}."),
    };

    // Read initial map.
    let mut minute = 0;
    let map = Map::from_file(&args.input);
    debug!("\nMinute: {minute}\nMap:{map}");

    // The way blizzards propagate, the maps will be periodic.
    // The period will be the lowest common multiple of the map width and map height.
    let nrows = map.grid.len();
    let ncols = map.grid[0].len();
    let period = (1..=(ncols * nrows))
        .skip_while(|n| n % nrows != 0 || n % ncols != 0)
        .next()
        .unwrap();

    // Compute all possible maps.
    let mut maps = Vec::from([map]);
    (1..period).for_each(|n| {
        let map_prev = &maps[n - 1];
        let map = map_prev.next_minute();
        maps.push(map);
    });
    info!("Precomputed {} maps.", maps.len());

    // Fully tracking all the possible paths until we reach the exit explodes.
    // For this we only keep track of the possible positions at each minute.
    //
    // Unlike the implementation in day24.rs, here we don't truncate positions
    // as soon as we reach the end of a crossing (way) in part 2.
    // This is to cover the case where two different paths for the first
    // crossing have times T_1 < S_1, but if we continue with the other
    // crossings, it will be S_1 + S_2 + S_3 < T_1 + T_2 + T_3.
    //
    // In the end, it turned out that this didn't matter. But it is not clear
    // if this is always the case, or it just happened to be that way for the
    // inputs we tried.
    let mut all_possible_positions = Vec::<Vec<Position>>::new();
    let mut targets = Vec::<Position>::new();
    for n in 0..nways {
        all_possible_positions.push(Vec::<Position>::new());
        targets.push(if n % 2 == 0 { maps[0].exit } else { maps[0].start });
    }
    all_possible_positions[0].push(maps[0].start);

    let mut done = false;
    while !done {
        minute += 1;
        let map = &maps[minute % period];
        let npositions: usize = all_possible_positions.iter().map(|w| w.len()).sum();
        info!("\nMinute: {minute}\nNumber of possible positions: {npositions}");

        // Update positions for all ways.
        all_possible_positions = all_possible_positions
            .iter()
            .enumerate()
            .map(|(way, possible_positions)| {
                let mut possible_positions = possible_positions
                    .iter()
                    .map(|position| map.available_moves(position))
                    .flatten()
                    .collect::<Vec<_>>();

                // Keeping track of all possible position still isn't enough.
                // We need to deduplicate the possible positions to keep things snappy.
                // Duplication arises because it is possible to reach the same position
                // through different paths in a set amount of time.
                possible_positions.sort();
                possible_positions.dedup();

                // After deduplication, sort possible positions by Manhattan order to
                // the exit. This makes the loop termination condition trivial.
                let target = targets[way];
                possible_positions.sort_by_key(|pos| {
                    let dx = (target.0 as i32 - pos.0 as i32).abs();
                    let dy = (target.1 as i32 - pos.1 as i32).abs();
                    dx + dy
                });

                if possible_positions.len() > 0 {
                    let closest = &possible_positions[0];
                    info!(
                        "Way: {way}, Positions: {}, Target: {target:?}, Closest position: {closest:?}",
                        possible_positions.len()
                    );
                }

                possible_positions
            })
            .collect::<Vec<_>>();

        // Move positions that reached target to the next way.
        let mut removed = Vec::<Position>::new();
        for (way, possible_positions) in all_possible_positions.iter_mut().enumerate() {
            // Move removed positions from previous way to the current one.
            if removed.len() > 0 {
                possible_positions.append(&mut removed);
            }

            // Repopulate removed.
            let target = &targets[way];
            removed.extend(possible_positions.drain_filter(|pos| pos == target));

            // Done, but finish loop first.
            if way == nways - 1 && removed.len() > 0 {
                done = true;
                continue;
            }
        }
    }

    info!("Exited after {minute} minutes.");
}
