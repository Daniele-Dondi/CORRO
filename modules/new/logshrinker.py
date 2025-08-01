def compute_selected_column_averages(file_path, chunk_size, selected_columns, output_path):
    import numpy as np

    chunk = []
    i=0
    with open(file_path, "r",encoding="utf-8", errors="ignore") as f, open(output_path, "w") as out:
        for line in f:
            i+=1
            try:
                values = line.strip().split("\t")
                numeric_values = [float(values[i]) for i in selected_columns]
            except:
                continue  # Skip problematic lines

            chunk.append(numeric_values)

            if len(chunk) == chunk_size:
                avg = np.mean(chunk, axis=0)
                out.write("\t".join(map(str, avg)) + "\n")
                chunk = []

        if chunk:
            avg = np.mean(chunk, axis=0)
            out.write("\t".join(map(str, avg)) + "\n")
    print("Read: "+str(i)+" lines")


compute_selected_column_averages(
    file_path="log.txt",
    chunk_size=100,
    selected_columns=[4],
    output_path="averages_output.txt"
)
