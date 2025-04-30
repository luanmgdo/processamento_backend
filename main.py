import os
import time
import textwrap
import warnings

# Concurrency: permite executar múltiplos arquivos em paralelo usando processos
from concurrent.futures import ProcessPoolExecutor, as_completed

# Bibliotecas para leitura e extração de texto
import PyPDF2
from bs4 import BeautifulSoup

# Configuração de diretórios
input_dir = 'Documentos'
output_dir = 'saidas'
relatorio_final_path = os.path.join(os.getcwd(), "relatorio_final.txt")
os.makedirs(output_dir, exist_ok=True)

# Suprimir avisos do PyPDF2 
warnings.filterwarnings("ignore", category=PyPDF2.errors.PdfReadWarning)

def process_file(filename):
    """
    Processa um único arquivo (PDF ou HTML):
    - Extrai o texto.
    - Salva o conteúdo em um arquivo .txt correspondente.
    - Retorna status e tempo de execução.
    """
    input_file_path = os.path.join(input_dir, filename)
    output_file_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.txt")
    start_time = time.time()

    try:
        # Leitura de arquivos PDF
        if filename.endswith('.pdf'):
            with open(input_file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = "\n".join(page.extract_text() or '' for page in reader.pages)

        # Leitura de arquivos HTML
        elif filename.endswith('.html'):
            with open(input_file_path, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'html.parser')
                text = soup.get_text()

        else:
            return ('error', filename, 0)  # Tipo de arquivo não suportado

        # Escrita do texto extraído no diretório de saída
        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.write(text)

        elapsed = time.time() - start_time
        return ('success', filename, elapsed)

    except Exception:
        # Em caso de erro no processamento do arquivo
        return ('error', filename, 0)

if __name__ == "__main__":
    # Início do cronômetro global
    start_global = time.time()

    # Inicialização de variaveis de métricas
    qtd_success_pdf = 0
    qtd_success_html = 0
    qtd_error = 0
    total_time_pdf = 0
    total_time_html = 0
    results = []

    # Criação de um pool de processos para processar os arquivos em paralelo
    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(process_file, filename) for filename in os.listdir(input_dir)]
        for future in as_completed(futures):
            results.append(future.result())    

    # Calculo de resultados
    for status, filename, duration in results:
        if status == 'success':
            if filename.endswith('.pdf'):
                qtd_success_pdf += 1
                total_time_pdf += duration
            elif filename.endswith('.html'):
                qtd_success_html += 1
                total_time_html += duration
        elif status == 'error':
            qtd_error += 1

    avg_time_pdf = total_time_pdf / qtd_success_pdf if qtd_success_pdf else 0
    avg_time_html = total_time_html / qtd_success_html if qtd_success_html else 0
    processing_time_global = time.time() - start_global

    # Relatório final
    relatorio = textwrap.dedent(f"""
        Arquivos processados com sucesso : {qtd_success_pdf + qtd_success_html}
        Arquivos com erro: {qtd_error}
        Tempo médio de processamento dos PDF's: {avg_time_pdf:.2f} segundos
        Tempo médio de processamento dos HTML's: {avg_time_html:.2f} segundos
        Tempo de processamento total: {processing_time_global:.2f} segundos
    """)

    with open(relatorio_final_path, 'w', encoding='utf-8') as f:
        f.write(relatorio)

    print("Processamento concluído com sucesso.")
