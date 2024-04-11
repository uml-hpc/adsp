from sys import stdin, stdout
from operator import itemgetter

class mtx2crs_handler(object):
    def __init__(self, mtx=None, out=None):
        self.__mtx = mtx
        self.__out = out

    def run(self):
        def check_header(hdr):
            hdr = hdr.split()
            return (len(hdr) == 5) and (hdr[0][0:2] == "%%") and \
                    (hdr[0][2:] == "MatrixMarket") and \
                    (hdr[1] == "matrix") and \
                    (hdr[2] == "coordinate") and \
                    (hdr[3] in ["pattern", "real", "integer"]) and \
                    (hdr[4] in ["general", "symmetric"])

        def get_matrix_type(hdr):
            return hdr.split()[4]

        infile = open(self.__mtx, "r") if self.__mtx else stdin
        outfile = open(self.__out, "w") if self.__out else stdout

        matrix_data = []
        matrix_dict = {}
        matrix_type = ""

        for count, line in enumerate(infile.readlines()):
            # remove leading and trailing whitespaces
            line = line.strip()

            # if we have a comment, ignore it
            if count == 0:
                if not check_header(line):
                    raise Exception('Invalid header')
                matrix_type = get_matrix_type(line)

            if line[0] == '%':
                continue

            # tokenize
            data = line.split()

            if len(matrix_data) == 0 and len(data) == 3:
                # if we do not have matrix data setup, set it up
                matrix_data = data
                continue

            # we have matrix data
            column = int(data[1])
            tup = (int(data[0]), 1.0 if len(data) == 2 else float(data[2]))

            if column in matrix_dict:
                # we already have this column on the dictionary, just add it
                matrix_dict[column].append(tup)
            else:
                # need to add a column to the dictionary
                matrix_dict[column] = [tup]


        # matrix information:
        # {g|s}: general or symmetric
        # columns
        # number of non-zero elements
        print(f"{matrix_type[0]}\n{matrix_data[1]}\n{matrix_data[2]}",
              file=outfile)

        mat = sorted(matrix_dict, key=lambda k: len(matrix_dict[k]), reverse=True)

        matrix = []


        for index in mat:
            matrix.append(matrix_dict[index])

        # jagged diagonals
        print(len(matrix[0]), file=outfile)

        value_list = []
        row_index = []
        start_position = [1]

        while len(matrix) > 0:
            matrix_temp = list(matrix)
            ri_ptr = 0;
            for cnt, entry in enumerate(matrix_temp):
                if len(entry) == 0:
                    continue

                ri_ptr += 1
                entry_temp = list(entry)
                val = entry_temp.pop(0)
                value_list.append(val[1])
                row_index.append(val[0])
                matrix[cnt] = entry_temp

            start_position.append(start_position[-1] + ri_ptr)
            matrix = [i for i in matrix if len(i) > 0]

        # number of elements in position array
        print(len(start_position), file=outfile)

        # permutation array size
        p_array = list(mat)
        for i in range(int(matrix_data[1])):
            if i + 1 not in mat:
                p_array.append(i+1)

        print(len(p_array), file=outfile)

        # value list
        print("\n".join(str(v) for v in value_list), file=outfile)

        # row index
        print("\n".join(str(r) for r in row_index), file=outfile)

        # permutation list
        print("\n".join(str(p) for p in p_array), file=outfile)

        # position array
        print("\n".join(str(s) for s in start_position), file=outfile)
