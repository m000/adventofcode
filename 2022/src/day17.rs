use clap::Parser;
use env_logger::Env;
use log::{debug, error, info, log_enabled, Level};
use std::cmp::{max, min};
use std::fmt;
use std::fs::File;
use std::io::{BufRead, BufReader};
use std::ops::Range;
use utf8_read::Reader;

/// Advent of Code 2022, Day 17
#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Args {
    /// Input file to read
    input: String,

    /// Part of the puzzle to solve
    #[arg(short, long, value_parser = clap::value_parser!(u32).range(1..=2))]
    part: u32,
}

const CHAMBER_WIDTH: usize = 7; // chamber width
const HOFFSET_START: usize = 2; // offset from left wall for new shapes
const VOFFSET_START: usize = 3; // offset from highest rock for new shapes
const SHAPE_MAX: u32 = 4;

#[derive(Clone)]
pub struct Bitmap {
    data: Vec<[bool; CHAMBER_WIDTH]>,
}

impl Bitmap {
    pub fn new(initial_height: Option<usize>) -> Bitmap {
        let mut bmp = Bitmap {
            data: Vec::<[bool; CHAMBER_WIDTH]>::new(),
        };
        for _ in 0..initial_height.unwrap_or(0) {
            bmp.data.push([false; CHAMBER_WIDTH]);
        }
        bmp
    }

    pub fn new_shape(type_: u32) -> Bitmap {
        // Read input shape.
        // We expect inputs to be trimmed of excessive top, left and bottom whitespace.
        let filename = format!("input/input17.shape{type_:02}.txt");
        let shape_lines = BufReader::new(File::open(&filename).unwrap_or_else(|err| {
            panic!("Error reading shape from {filename}: {err:?}");
        }))
        .lines()
        .enumerate()
        .map(|(lineno, line)| {
            let lineno_1 = lineno + 1;
            line.unwrap_or_else(|err| {
                panic!("Cannot read at {filename}:{lineno_1}: {err:?}");
            })
        })
        .collect::<Vec<_>>();

        // Put shape in a bitmap.
        let mut bmp = Bitmap::new(Some(shape_lines.len()));
        shape_lines.iter().rev().enumerate().for_each(|(i, line)| {
            line.chars()
                .enumerate()
                .filter(|(_j, c)| c == &'#')
                .for_each(|(j, _c)| {
                    bmp.data[i][j] = true;
                });
        });

        // Check for trailing empty lines.
        match bmp.vmin() {
            Some(0) => {}
            _ => {
                panic!("Trailing empty lines in shape read from {filename}.");
            }
        }

        // Check for heading empty lines.
        match bmp.vmax() {
            Some(vmax) => {
                if vmax != bmp.data.len() - 1 {
                    panic!("Heading empty lines in shape read from {filename}.");
                }
            }
            _ => {
                panic!("Heading empty lines in shape read from {filename}.");
            }
        }

        // Horizontally shift shape into starting position.
        bmp.hshift(HOFFSET_START as i64);
        debug!("Read shape from {filename}: {bmp:?}");
        bmp
    }

    /// Returns the minimum horizontal position in the bitmap.
    pub fn hmin(&self) -> Option<usize> {
        self.data
            .iter()
            .map(|row| {
                row.iter()
                    .enumerate()
                    .skip_while(|(_j, v)| v == &&false)
                    .map(|(j, _v)| j)
                    .next()
            })
            .filter(|min_row| !min_row.is_none()) // skip empty rows
            .min()
            .unwrap_or(None) // None -> empty bitmap
    }

    /// Returns the maximum horizontal position in the bitmap.
    pub fn hmax(&self) -> Option<usize> {
        self.data
            .iter()
            .map(|row| {
                row.iter()
                    .enumerate()
                    .rev() // start scanning from the end of row
                    .skip_while(|(_j, v)| v == &&false)
                    .map(|(j, _v)| j)
                    .next()
            })
            .filter(|max_row| !max_row.is_none()) // skip empty rows
            .max()
            .unwrap_or(None) // None -> empty bitmap
    }

    /// Returns the index of the lower-most non-empty row in the bitmap.
    pub fn vmin(&self) -> Option<usize> {
        self.data
            .iter()
            .enumerate()
            .skip_while(|(_i, row)| row.iter().all(|v| !v))
            .map(|(i, _row)| i)
            .next()
    }

    /// Returns the index of the top-most non-empty row in the bitmap.
    pub fn vmax(&self) -> Option<usize> {
        self.data
            .iter()
            .enumerate()
            .rev()
            .skip_while(|(_i, row)| row.iter().all(|v| !v))
            .map(|(i, _row)| i)
            .next()
    }

    /// Horizontally shifts the bitmap by the specified offset,
    /// guarding for overflows.
    pub fn hshift(&mut self, n: i64) {
        // Calculate which part of the bitmap needs to be copied.
        let (hmin, hmax) = (self.hmin(), self.hmax());

        // Calculate the actual shift.
        let shift = if n > 0 && !hmax.is_none() {
            // right shift
            min(n, (CHAMBER_WIDTH - 1 - hmax.unwrap()) as i64)
        } else if n < 0 && !hmin.is_none() {
            // left shift
            max(n, -(hmin.unwrap() as i64))
        } else {
            // empty bitmap or bitmap adjacent to an edge
            0
        };

        if shift == 0 {
            return;
        }

        let (hmin, hmax) = (hmin.unwrap(), hmax.unwrap());
        self.data.iter_mut().for_each(|row| {
            // Copy row to the right position.
            let copy_to = (hmin as i64 + shift) as usize;
            row.copy_within(hmin..=hmax, copy_to);

            // Clear data outsite copied range.
            row[0..copy_to].fill(false);
            row[(copy_to + 1 + (hmax - hmin))..].fill(false);
        });
    }

    /// Adds enough room to self, for shape to start falling.
    /// Returns the height (base-0) at which the shape should start its fall.
    /// Shapes are expected to not have trailing empty lines.
    pub fn grow_to_fit(&mut self, shape: &Bitmap) -> usize {
        let vmax = self.vmax();
        let shape_height = shape.data.len();
        let start_height = match vmax {
            Some(vmax) => vmax as i64,
            None => -1,
        } + 1
            + VOFFSET_START as i64;

        let grow_by = max(0, start_height + shape_height as i64 - self.data.len() as i64);
        debug!("Growing bitmap by {grow_by} to fit next shape.");
        for _ in 0..grow_by {
            self.data.push([false; CHAMBER_WIDTH]);
        }

        start_height as usize
    }

    /// Check if self overlaps with shape, if shape is placed at height.
    pub fn overlaps(&self, shape: &Bitmap, height: usize) -> bool {
        let row_overlaps = self
            .data
            .iter()
            .skip(height) // start at height
            .take(shape.data.len()) // only check as many rows as shape's height
            .zip(shape.data.iter()) // zip rows in pairs
            .map(|(self_row, shape_row)| {
                // zip values in each pair of rows and check for overlaps
                self_row
                    .iter()
                    .zip(shape_row.iter())
                    .any(|(self_v, shape_v)| self_v == &true && shape_v == &true)
            })
            .collect::<Vec<_>>();
        debug!("Overlap check at height {height}: {shape:?} {self:?}\nRow overlaps: {row_overlaps:?}");
        row_overlaps.iter().any(|row_overlaps| row_overlaps == &true)
    }

    /// Places the shape over self, at the specified height.
    pub fn place(&mut self, shape: &Bitmap, height: usize) {
        self.data
            .iter_mut()
            .skip(height) // start at height
            .take(shape.data.len()) // only process as many rows as shape's height
            .zip(shape.data.iter()) // zip rows in pairs
            .for_each(|(self_row, shape_row)| {
                self_row.iter_mut().enumerate().for_each(|(i, vref)| {
                    *vref |= shape_row[i];
                })
            });
        debug!("Placed shape at height {height}: {shape:?} {self:?}");
    }
}

impl fmt::Debug for Bitmap {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let vmax = self.vmax();
        write!(
            f,
            "\nBitmap {}×{CHAMBER_WIDTH}\n{}",
            self.data.len(),
            self.data
                .iter()
                .enumerate()
                .rev()
                .map(|(i, row)| {
                    format!(
                        "{i:>4}{}{}\n",
                        match vmax {
                            Some(vmax) =>
                                if vmax == i {
                                    '→'
                                } else {
                                    ' '
                                },
                            None => {
                                ' '
                            }
                        },
                        row.iter().map(|v| if *v { '█' } else { '░' }).collect::<String>()
                    )
                })
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

    // Set number of iterations.
    let iterations: usize = match args.part {
        1 => 2022,
        2 => 1000000000000,
        part @ _ => panic!("Don't know how to run part {part}."),
    };

    // Read shapes.
    let shapes = Range {
        start: 0,
        end: SHAPE_MAX + 1,
    }
    .map(|i| Bitmap::new_shape(i))
    .collect::<Vec<_>>();

    // Make cyclic cloning iterator for shapes.
    let mut shapes = shapes.iter().cycle().cloned();

    // Initialize chamber.
    let mut chamber = Bitmap::new(None);

    // Create input iterator for shift ops.
    let filename = &args.input;
    let input_base = Reader::new(BufReader::new(File::open(filename).unwrap_or_else(|err| {
        panic!("Error opening {filename}: {err:?}");
    })))
    .into_iter()
    .enumerate()
    .map(|(i, x)| {
        let i_1 = i + 1;
        (
            i_1,
            x.unwrap_or_else(|err| panic!("Error reading {filename}:C{i}: {err:?}")),
        )
    })
    .filter(|(_i_1, x)| match x {
        '>' | '<' => true,
        _ => false,
    })
    .collect::<Vec<_>>();
    let mut input = input_base.iter().cycle();

    for ndropped in 0..iterations {
        let mut shape = shapes.next().unwrap();
        let h = chamber.grow_to_fit(&shape);

        if log_enabled!(Level::Debug) {
            debug!("Dropping shape {ndropped:05}: {shape:?} {chamber:?}");
        } else {
            info!("Dropping shape {ndropped:05}: {shape:?}");
        }
        for try_h in (0..=h).rev() {
            if chamber.overlaps(&shape, try_h) {
                // overlap detected
                debug!("Placing at height {}.", try_h + 1);
                chamber.place(&shape, try_h + 1);
                break;
            }

            // Not placed. Shift.
            let (i_1, shift_op) = input.next().unwrap();
            debug!("Shifting with {shift_op:?} at height {try_h}.");
            let shift = match shift_op {
                '>' => 1,
                '<' => -1,
                _ => panic!("Unknown shift op at character {i_1}: {shift_op:?}"),
            };
            shape.hshift(shift);

            if chamber.overlaps(&shape, try_h) {
                // overlap after shift
                debug!("Canceling previous shift at height {try_h}.");
                shape.hshift(-shift);
            }

            if try_h == 0 {
                // reached bottom
                debug!("Placing at height {try_h}.");
                chamber.place(&shape, 0);
            }
        }
        let ndropped_1 = ndropped + 1;
        if iterations < 10000 && log_enabled!(Level::Info) {
            info!(
                "Dropped {ndropped_1} shapes. Rock tower is {} units tall.",
                chamber.vmax().unwrap() + 1
            );
        } else if (ndropped_1 % 10000 == 0) && log_enabled!(Level::Error) {
            error!(
                "Dropped {ndropped_1} shapes. Rock tower is {} units tall.",
                chamber.vmax().unwrap() + 1
            );
        }
    }
}
