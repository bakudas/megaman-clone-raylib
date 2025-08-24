# analyze_profile.py
import pstats

# Carrega o arquivo de estatísticas que geramos
p = pstats.Stats('profile_stats')

# Limpa os nomes dos arquivos e ordena pelo tempo cumulativo gasto em cada função
p.strip_dirs().sort_stats('cumulative').print_stats(20)

# 'cumulative' é a métrica mais importante: ela mostra o tempo total
# gasto em uma função MAIS o tempo de todas as funções que ela chamou.
# O topo desta lista é o nosso maior gargalo.