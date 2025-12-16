from sudoku.board import Board

def test_board_validity_and_candidates():
    b = Board.from_lines([
        "530070000",
        "600195000",
        "098000060",
        "800060003",
        "400803001",
        "700020006",
        "060000280",
        "000419005",
        "000080079",
    ])
    assert b.is_valid()
    assert len(b.candidates(0, 2)) > 0
    assert len(b.candidates(0, 0)) == 0