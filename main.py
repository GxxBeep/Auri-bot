import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os


# Instância do bot
class AuriMain(commands.Bot):
    def __init__(self, *args, **kwargs):
        """
        Inicializa a classe principal do bot Auri.

        Args:
            *args: Argumentos posicionais.
            **kwargs: Argumentos nomeados. Inclui configurações como `command_prefix`.
        """
        super().__init__(*args, **kwargs, command_prefix=".",)

    async def on_ready(self):
        """
        Método executado quando o bot está pronto.

        - Carrega as extensões localizadas na pasta `./cogs`.
        - Sincroniza os comandos da árvore de comandos do bot.
        - Exibe informações sobre o estado do bot e extensões carregadas no terminal.
        """
        x = 0  # Inicializa um contador para rastrear o número de extensões carregadas.
        for f in os.listdir("./cogs"):  # Itera sobre os arquivos na pasta "./cogs".
            if f != "__init__.py": # Verifica se o arquivo não é o __init__.py
                if f.endswith(".py"):  # Verifica se o arquivo tem a extensão ".py".
                    try:
                        # Carrega a extensão usando o nome do arquivo sem a extensão ".py".
                        await bot.load_extension("cogs." + f[:-3])
                        print(f"Extensão carregada: cogs.{f[:-3]}")
                        x += 1  # Incrementa o contador de extensões carregadas.
                    except Exception as e:
                        # Captura e exibe qualquer erro que ocorra durante o carregamento da extensão.
                        print(f"Erro ao carregar cogs.{f[:-3]}: {e}")
        print(f"\nExtensões carregadas: {x}")
         
        try:
            synced = await self.tree.sync(guild=discord.Object(id=1210623174673432626))  # Sincroniza os comandos do bot com o servidor Discord.
            print(f"Sincronizado {len(synced)} comandos")
        except Exception as e:
            # Captura e exibe erros que possam ocorrer durante a sincronização.
            print(f"Erro ao sincronizar comandos: {e}")
        print(f"Bot conectado como {bot.user}")
        
# Instância do bot com todas as intents habilitadas
bot = AuriMain(intents=discord.Intents.all())

# Define o comando 'ping' com nome e descrição
@bot.tree.command(name="ping", description="Responde com 'Pong!' e a latência do bot.") 
async def ping(interaction: discord.Interaction):
    """
    Comando 'ping'.
    
    Responde ao usuário com 'Pong!' seguido da latência do bot em milissegundos.
    
    Args:
        interaction (discord.Interaction): A interação que invocou o comando.
    """
    latency = round(bot.latency * 1000)  # Calcula a latência em milissegundos
    await interaction.response.send_message(f"Pong! Latência: {latency}ms")

# Função de autocomplete para o comando 'reload'
async def reload_autocomplete(interaction: discord.Interaction, current: str):
    """
    Fornece sugestões de autocomplete baseadas no termo digitado pelo usuário, buscando nas extensões do bot.

    Esta função é usada para gerar opções de autocomplete durante a interação com comandos de barra (slash commands),
    sugerindo as extensões carregadas no bot que correspondem ao termo `current`.

    Args:
        interaction (discord.Interaction): O objeto de interação que contém informações sobre a interação do usuário.
        current (str): O termo digitado pelo usuário para buscar correspondências nas extensões.

    Returns:
        list: Uma lista de objetos `app_commands.Choice` contendo as extensões que correspondem ao termo `current`.
              Cada objeto `Choice` tem um `name` e `value` igual ao nome da extensão, sem o prefixo "cogs.".
    """
    cogs_list = []  # Lista para armazenar as extensões que correspondem ao termo de busca.
    for ext in bot.extensions:  # Itera sobre todas as extensões carregadas no bot.
        if current.lower() in ext.lower():  # Verifica se o termo 'current' está presente no nome da extensão, ignorando maiúsculas/minúsculas.
            ext = ext.replace("cogs.", "")  # Remove o prefixo "cogs." do nome da extensão.
            cogs_list.append(app_commands.Choice(name=ext, value=ext))  # Adiciona a extensão à lista como uma sugestão de autocomplete.
    return cogs_list  # Retorna a lista de sugestões baseadas no termo 'current'.

@bot.tree.command(name="reload", description="Recarrega as extensões do bot.") # Define o comando 'reload'
@app_commands.describe(extension="Extensão a ser recarregada.") # Define a descrição do argumento 'extension'
@app_commands.autocomplete(extension=reload_autocomplete) # Define o autocomplete para o argumento 'extension'
async def reload_cogs(interaction: discord.Interaction, extension: str):
    """
    Comando para recarregar uma extensão do bot.

    Este comando permite que o usuário recarregue uma extensão específica do bot sem precisar reiniciar o bot inteiro.
    O comando verifica se a extensão existe, tenta descarregá-la e carregá-la novamente, e responde com uma mensagem
    informando o sucesso ou falha do processo.

    Args:
        interaction (discord.Interaction): O objeto de interação que contém informações sobre a interação do usuário.
        extension (str): O nome da extensão (cog) a ser recarregada. O nome deve ser fornecido sem o prefixo "cogs.".

    Returns:
        None: O comando envia uma resposta diretamente à interação, sem retornar nada explicitamente.
    """
    extension = "cogs." + extension  # Adiciona o prefixo "cogs." ao nome da extensão.

    if extension not in bot.extensions:  # Verifica se a extensão está carregada no bot.
        await interaction.response.send_message(f"⚠️ A extensão `{extension}` não existe.")  # Informa se a extensão não foi encontrada.
        return
    
    try:
        await bot.unload_extension(extension)  # Descarrega a extensão.
        await bot.load_extension(extension)  # Recarrega a extensão.
        await interaction.response.send_message(f"🔄 Extensão `{extension}` recarregada com sucesso.")  # Informa o sucesso.
    except Exception as e:  # Captura qualquer erro durante o processo de recarregamento.
        await interaction.response.send_message(f"⚠️ Falha ao recarregar `{extension}`:\n```{e}```")  # Exibe o erro ocorrido.

load_dotenv() # Carrega o arquivo .env
bot.run(os.getenv("TOKEN")) # Executa o bot