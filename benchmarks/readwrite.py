import os
import timeit
import uppaalpy
import lxml.etree as LET
import xml.etree.cElementTree as CET

def list_nta_in_dir(directory):
    return [directory.strip('/') + '/' + x \
            for x in os.listdir(directory) if x.endswith('.xml')]

def benchmark_read(files):
    for f in files:
        temp = uppaalpy.core.NTA.from_xml(f)

def benchmark_pretty_print(ntas):
    for nta in ntas:
        nta.to_file('/tmp/out_benchmark.xml', pretty=True)

def benchmark_write(ntas):
    for nta in ntas:
        nta.to_file('/tmp/out_benchmark.xml', pretty=False)

def benchmark_lxml_read(files):
    for f in files:
        temp = LET.parse(f)

def benchmark_cet_read(files):
    for f in files:
        temp = CET.parse(f)

# cElementTree and lxml share the same API for writing.
def benchmark_xml_write(trees):
    for tree in trees:
        tree.write('/tmp/out_benchmark.xml')

# Can only be used for lxml trees.
def benchmark_xml_write_pretty(trees):
    for tree in trees:
        tree.write('/tmp/out_benchmark.xml', pretty_print=True)

if __name__ == '__main__':

    files = list_nta_in_dir('examples/generator')
    lit_files = list_nta_in_dir('examples/literature')

    print()
    print("===============================")
    print()
    print("cElementTree benchmarks")
    print("Benchmarking cElementTree parse method.")

    start = timeit.default_timer()
    benchmark_cet_read(files)
    end = timeit.default_timer()

    start2 = timeit.default_timer()
    benchmark_cet_read(lit_files)
    end2 = timeit.default_timer()
    print("Read \t%s generator files in \t%s seconds." % (len(files), end - start))
    print("\t%s literature files in \t%s seconds." % (len(lit_files), end2 - start2))
    print()

    print("Benchmarking cElementTree write method")

    trees = [CET.parse(f) for f in files]
    lit_trees = [CET.parse(f) for f in lit_files]

    start = timeit.default_timer()
    benchmark_xml_write(trees)
    end = timeit.default_timer()

    start2 = timeit.default_timer()
    benchmark_xml_write(lit_trees)
    end2 = timeit.default_timer()

    print("Wrote \t%s generator files in \t%s seconds." % (len(files), end - start))
    print("\t%s literature files in \t%s seconds." % (len(lit_files), end2 - start2))
    print()
    print("===============================")
    print()
    
    print("lxml benchmarks")
    print("Benchmarking lxml parse method.")

    start = timeit.default_timer()
    benchmark_lxml_read(files)
    end = timeit.default_timer()

    start2 = timeit.default_timer()
    benchmark_lxml_read(lit_files)
    end2 = timeit.default_timer()
    print("Read \t%s generator files in \t%s seconds." % (len(files), end - start))
    print("\t%s literature files in \t%s seconds." % (len(lit_files), end2 - start2))
    print()

    trees = [LET.parse(f) for f in files]
    lit_trees = [LET.parse(f) for f in lit_files]

    print("Benchmarking lxml write method")
    start = timeit.default_timer()
    benchmark_xml_write(trees)
    end = timeit.default_timer()

    start2 = timeit.default_timer()
    benchmark_xml_write(lit_trees)
    end2 = timeit.default_timer()

    print("Wrote \t%s generator files in \t%s seconds." % (len(files), end - start))
    print("\t%s literature files in \t%s seconds." % (len(lit_files), end2 - start2))
    print()


    print("Benchmarking lxml write method (pretty)")
    start = timeit.default_timer()
    benchmark_xml_write_pretty(trees)
    end = timeit.default_timer()

    start2 = timeit.default_timer()
    benchmark_xml_write_pretty(lit_trees)
    end2 = timeit.default_timer()

    print("Wrote \t%s generator files in \t%s seconds." % (len(files), end - start))
    print("\t%s literature files in \t%s seconds." % (len(lit_files), end2 - start2))
    print()
    print("===============================")
    print()





    print("Benchmarking from_xml method.")
    start = timeit.default_timer()
    benchmark_read(files)
    end = timeit.default_timer()

    start2 = timeit.default_timer()
    benchmark_read(lit_files)
    end2 = timeit.default_timer()
    print("Read \t%s generator files in \t%s seconds." % (len(files), end - start))
    print("\t%s literature files in \t%s seconds." % (len(lit_files), end2 - start2))

    print()

    ntas = []
    for f in files:
        ntas.append(uppaalpy.core.NTA.from_xml(f))

    print("Benchmarking to_xml method (ugly).")
    start = timeit.default_timer()
    benchmark_write(ntas)
    end = timeit.default_timer()

    start2 = timeit.default_timer()
    benchmark_write(ntas)
    end2 = timeit.default_timer()

    print("Wrote \t%s generator files in \t%s seconds." % (len(files), end - start))
    print("\t%s literature files in \t%s seconds." % (len(lit_files), end2 - start2))

    print()

    print("Benchmarking to_xml method (pretty).")
    start = timeit.default_timer()
    benchmark_pretty_print(ntas)
    end = timeit.default_timer()

    start2 = timeit.default_timer()
    benchmark_pretty_print(ntas)
    end2 = timeit.default_timer()

    print("Wrote \t%s generator files in \t%s seconds." % (len(files), end - start))
    print("\t%s literature files in \t%s seconds." % (len(lit_files), end2 - start2))

    print()
