import os
import timeit
import uppaalpy

def list_nta_in_dir(directory):
    return [directory.strip('/') + '/' + x \
            for x in os.listdir(directory) if x.endswith('.xml')]

def benchmark_read(files):
    for f in files:
        temp = uppaalpy.core.NTA.from_xml(f)

def benchmark_pretty_print(ntas):
    for nta in ntas:
        nta.to_file('/tmp/out_benchmark.xml', pretty = True)

def benchmark_write(ntas):
    for nta in ntas:
        nta.to_file('/tmp/out_benchmark.xml', pretty = False)

if __name__ == '__main__':

    files = list_nta_in_dir('examples/generator')
    lit_files = list_nta_in_dir('examples/literature')
    
    print("Generator tests")
    print("Benchmarking from_xml method.")
    start = timeit.default_timer()
    benchmark_read(files)
    end = timeit.default_timer()

    print("Read %s files in %s seconds." % (len(files), end - start))

    print()

    ntas = []
    for f in files:
        ntas.append(uppaalpy.core.NTA.from_xml(f))

    print("Benchmarking to_xml method (pretty).")
    start = timeit.default_timer()
    benchmark_pretty_print(ntas)
    end = timeit.default_timer()

    print("Wrote %s files in %s seconds." % (len(files), end - start))

    print()

    print("Benchmarking to_xml method (ugly).")
    start = timeit.default_timer()
    benchmark_write(ntas)
    end = timeit.default_timer()

    print("Wrote %s files in %s seconds." % (len(files), end - start))

    print()
    print("Literature tests")
    print("Benchmarking from_xml method.")
    start = timeit.default_timer()
    benchmark_read(lit_files)
    end = timeit.default_timer()

    print("Read %s files in %s seconds." % (len(lit_files), end - start))

    print()

    ntas = []
    for f in lit_files:
        ntas.append(uppaalpy.core.NTA.from_xml(f))

    print("Benchmarking to_xml method (pretty).")
    start = timeit.default_timer()
    benchmark_pretty_print(ntas)
    end = timeit.default_timer()

    print("Wrote %s files in %s seconds." % (len(lit_files), end - start))

    print()

    print("Benchmarking to_xml method (ugly).")
    start = timeit.default_timer()
    benchmark_write(ntas)
    end = timeit.default_timer()

    print("Wrote %s files in %s seconds." % (len(lit_files), end - start))

