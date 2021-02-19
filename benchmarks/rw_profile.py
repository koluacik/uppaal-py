#from benchmarks.readwrite import *
#from .readwrite import *
from readwrite import *
import cProfile
import pstats
from pstats import SortKey

if __name__ == '__main__':
    files = list_nta_in_dir('examples/generator')
    lit_files = list_nta_in_dir('examples/literature')
    cProfile.run('benchmark_read(files)', 'benchmarks/read_stats')
    cProfile.run('benchmark_read(lit_files)', 'benchmarks/lit_read_stats')

    ntas = []
    for f in files:
        ntas.append(uppaalpy.core.NTA.from_xml(f))

    lit_ntas = []
    for f in lit_files:
        lit_ntas.append(uppaalpy.core.NTA.from_xml(f))

    cProfile.run('benchmark_write(ntas)', 'benchmarks/write_stats')
    cProfile.run('benchmark_write(lit_ntas)', 'benchmarks/lit_write_stats')

    rstats = pstats.Stats('benchmarks/read_stats')
    lrstats = pstats.Stats('benchmarks/lit_read_stats')

    wstats = pstats.Stats('benchmarks/write_stats')
    lwstats = pstats.Stats('benchmarks/lit_write_stats')

    #rstats.strip_dirs().sort_stats(SortKey.CUMULATIVE).print_stats()
    #lrstats.strip_dirs().sort_stats(SortKey.CUMULATIVE).print_stats()
    #wstats.strip_dirs().sort_stats(SortKey.CUMULATIVE).print_stats()
    lwstats.strip_dirs().sort_stats(SortKey.CUMULATIVE).print_stats()
