import shlex
import subprocess
import re

def run_ntJoin(file1, file2, prefix, window=1000):
    cmd = "../ntJoin assemble -B list_files=\'" + file1 + " " + file2 + "\' " \
          "list_weights=\'2 1\' k=32 w=" + str(window) + " n=2 prefix=" + prefix
    cmd_shlex = shlex.split(cmd)
    return_code = subprocess.call(cmd_shlex)
    assert return_code == 0
    return_paths = []
    with open(prefix + ".path", 'r') as paths:
        for line in paths:
            path_match = re.search(r'^mx', line)
            if path_match:
                return_paths.append(line.strip())
    return return_paths


'''Following 4 tests to check for the expected PATHs given 2 pieces that should be merged
    together based on the reference in different orientations
    - Pieces are the reference piece split, with ~20bp in between
'''
def test_mx_f_f():
    paths = run_ntJoin("ref.fa", "scaf.f-f.fa", "f-f_test")
    assert len(paths) == 1
    assert paths.pop() == "mx0\t1_f+:0-1981 20N 2_f+:0-2329"


def test_mx_f_r():
    paths = run_ntJoin("ref.fa", "scaf.f-r.fa", "f-r_test")
    assert len(paths) == 1
    assert paths.pop() == "mx0\t1_f+:0-1981 20N 2_r-:0-2329"


def test_mx_r_f():
    paths = run_ntJoin("ref.fa", "scaf.r-f.fa", "r-f_test")
    assert len(paths) == 1
    assert paths.pop() == "mx0\t1_r-:0-1981 20N 2_f+:0-2329"


def test_mx_r_r():
    paths = run_ntJoin("ref.fa", "scaf.r-r.fa", "r-r_test")
    assert len(paths) == 1
    assert paths.pop() == "mx0\t1_r-:0-1981 20N 2_r-:0-2329"

'''
Test checks for the expected gap length and sequence orientation for a 
test with 2 expected output paths
'''
def test_gap_dist_multiple():
    paths = run_ntJoin("ref.multiple.fa", "scaf.multiple.fa", "gap-dist_test", 500)
    assert len(paths) == 2
    assert paths[0] != paths[1]
    expected_paths = ["2_1_p+:0-2492 100N 2_2_n-:0-2574", "1_1_p+:0-1744 124N 1_2_p+:0-1844"]
    assert paths.pop().split("\t")[1] in expected_paths
    assert paths.pop().split("\t")[1] in expected_paths


'''
Tests for gap distance estimation, misassembled scaffolds
Expected that 2 input scaffolds will be broken and joined based on the reference.
Testing orientations of joins: +/+ -/- +/- -/+
'''
def test_regions_ff_rr():
    paths = run_ntJoin("ref.multiple.fa", "scaf.misassembled.f-f.r-r.fa", "regions-ff-rr_test", 500)
    assert len(paths) == 2
    assert paths[0] != paths[1]
    expected_paths = ["2_1n-1_2p-:0-2176 20N 1_1p-2_2n-:2010-4489", "1_1p-2_2n+:0-1541 468N 2_1n-1_2p+:2676-4379"]
    assert paths.pop().split("\t")[1] in expected_paths
    assert paths.pop().split("\t")[1] in expected_paths


def test_regions_fr_rf():
    paths = run_ntJoin("ref.multiple.fa", "scaf.misassembled.f-r.r-f.fa", "regions-fr-rf_test", 500)
    assert len(paths) == 2
    assert paths[0] != paths[1]
    expected_paths = ["2_1n-1_2n-:0-2176 212N 1_1p-2_2p+:2017-4489", "1_1p-2_2p+:0-1617 198N 2_1n-1_2n-:2675-4379"]
    assert paths.pop().split("\t")[1] in expected_paths
    assert paths.pop().split("\t")[1] in expected_paths
