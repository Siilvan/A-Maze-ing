# Project Requirements
- Maze generation should be part of a unique class "MazeGenerator"
- Unique maze generation class must be within a standalone module
- The entire reusable module must be available in a single file for later pip install
- Use .tar.gz or .whl format for module
- LICENSE.md

# TODO
- [x] Maze modeling
    - [ ] Cell representation (code)
    - [ ] Maze representation (code)
- [x] Configuration parsing
    - [x] Key value pair setting
    - [x] Invalid pair handling
    - [x] Comment handling
- [x] Perfect maze gen algorithm
- [x] Non-perfect maze gen algorithm
- [ ] Unit tests
- [x] Visual maze representation (MiniLibX or ASCII) (arguably)
- [ ] Visual display user interaction
    - [ ] Maze regeneration 
    - [ ] Show/hide shortest path to exit
    - [ ] Change wall colors
    - [ ] (optional) set specific color for the 42 pattern

# Edge cases

- [ ] Ensure entry and exit are different
- [ ] Ensure full connectivity and no unreachable cells (omitting the 42)
- [ ] Ensure border cells all have walls
- [ ] Ensure corridors can't be larger than 2 cells.
- [ ] Ensure maze contains **exactly** one path on "PERFECT"
