import os
from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from time import sleep

# Configuração do banco de dados
db = create_engine("sqlite:///banco.db", echo=True)
Session = sessionmaker(bind=db)
session = Session()
Base = declarative_base()

salao_preserva = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
usuario_autenticado = None

# Definindo as classes de clientes e reservas
class Clientes(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, nullable=False)
    cpf = Column(String, nullable=False, unique=True)
    password_hash = Column(String(256), nullable=False)

    def __init__(self, nome, cpf, password):
        self.nome = nome
        self.cpf = cpf
        self.set_password(password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Reserva(Base):
    __tablename__ = "reservas"

    id = Column(Integer, autoincrement=True, primary_key=True)
    salao = Column(Integer, nullable=False)
    dono = Column(ForeignKey("clientes.id"), nullable=False)
    data_pedido = Column(DateTime, default=datetime.utcnow, nullable=False)
    data_reserva = Column(DateTime, nullable=False)

Base.metadata.create_all(db)

# ---------------------------usuário-----------------------------------
# Menu principal
def menu_principal():
    os.system("cls")
    menu = """
    ╔══════════════════════════╗
    ║       MENU PRINCIPAL     ║
    ╠══════════════════════════╣
    ║ [1] Registrar usuário    ║
    ║ [2] Entrar               ║
    ║ [3] Sair                 ║
    ╚══════════════════════════╝
    """
    print(menu)
    opcao = input("Escolha uma opção: ")

    if opcao == "1":
        registrar_usuario()
    elif opcao == "2":
        entrar_usuario()
    elif opcao == "3":
        print("Saindo...")
        return False
    else:
        print("Opção inválida!")
        sleep(2)
        menu_principal()

# Cadastro
def registrar_usuario():
    os.system("cls")
    nome = input("Digite seu nome: ")
    cpf = input("Digite seu CPF: ")
    senha = input("Digite sua senha: ")

    if session.query(Clientes).filter_by(cpf=cpf).first():
        os.system("cls")
        print("Erro: CPF já cadastrado!")
        sleep(2)
        menu_principal()

    novo_cliente = Clientes(nome=nome, cpf=cpf, password="")
    novo_cliente.set_password(senha)

    session.add(novo_cliente)
    session.commit()
    print("Usuário cadastrado com sucesso!")
    sleep(2)
    menu_principal()

# Login
def entrar_usuario():
    global usuario_autenticado
    os.system("cls")

    cpf = input("Digite seu CPF: ")
    senha = input("Digite sua senha: ")

    cliente = session.query(Clientes).filter_by(cpf=cpf).first()
    if not cliente:
        os.system("cls")
        print("Erro: Usuário não encontrado!")
        input("Preciose 'ENTER' para voltar...")
        menu_principal()

    if cliente.check_password(senha):
        os.system("cls")
        usuario_autenticado = cliente
        print(f"Bem-vindo, {usuario_autenticado.nome}!")
        sleep(2)
        menu_reserva()
    else:
        os.system("cls")
        print("Erro: Senha incorreta!")
        sleep(2)
        menu_principal()

#--------------------------reserva------------------------------------

# Menu de reserva
def menu_reserva():
    os.system("cls")
    menu = """
    ╔══════════════════════════╗
    ║       MENU DE RESERVAS   ║
    ╠══════════════════════════╣
    ║ [1] Fazer uma reserva    ║
    ║ [2] Excluir reserva      ║
    ║ [3] Ver locações         ║
    ║ [4] Editar locações      ║
    ║ [5] Sair                 ║
    ╚══════════════════════════╝
    """
    print(menu)
    opcao = input("Escolha uma opção: ")

    if opcao == "1":
        fazer_reserva()
    elif opcao == "2":
        excluir_reserva()
    elif opcao == "3":
        ver_locacoes()
    elif opcao == "4":
        editar_locacoes()
    elif opcao == "5":
        print("Saindo...")
        return False
    else:
        print("Opção inválida!")
        sleep(2)
        menu_reserva()

# Fazer reserva
def fazer_reserva():
    os.system("cls")
    global usuario_autenticado

    if not usuario_autenticado:
        print("Você precisa estar autenticado para fazer uma reserva.")
        sleep(2)
        return

    for i, salao in enumerate(salao_preserva, start=1):
        print(f"➡ {i} - Salão {salao}")

    try:
        escolha_salao = int(input("Digite o número do salão para a reserva: "))
        if escolha_salao < 1 or escolha_salao > len(salao_preserva):
            print("Erro: Escolha um salão válido!")
            sleep(2)
            return

        escolha_data = input("Digite a data da reserva (DD/MM/YYYY): ")
        data_obj = datetime.strptime(escolha_data, "%d/%m/%Y").date()

        data_atual = datetime.today().date()
        if data_obj <= data_atual:
            print("Erro: A data precisa ser no futuro!")
            sleep(2)
            menu_reserva()

        # Verefica se já existe uma reserva 
        reserva_existente = session.query(Reserva).filter_by(salao=escolha_salao, data_reserva=data_obj).first()
        if reserva_existente:
            os.system("cls")
            print("Erro: Já existe uma reserva para esse salão nesse dia!")
            sleep(2)
            return

        nova_reserva = Reserva(salao=escolha_salao, data_reserva=data_obj, dono=usuario_autenticado.id)
        session.add(nova_reserva)
        session.commit()

        print(f"Reserva confirmada para o Salão {escolha_salao} no dia {data_obj.strftime('%d/%m/%Y')}!")
        sleep(2)
        menu_reserva()

    except ValueError:
        print("Erro: Formato de data inválido! Use DD/MM/YYYY.")
        sleep(2)
        menu_reserva()

# Excluir
def excluir_reserva():
    os.system("cls")
    global usuario_autenticado

    if not usuario_autenticado:
        print("Você precisa estar autenticado para excluir uma reserva.")
        sleep(2)
        return

    reservas = session.query(Reserva).filter_by(dono=usuario_autenticado.id).all()
    if not reservas:
        os.system("cls")
        print("Você não tem reservas para excluir.")
        sleep(2)
        menu_reserva()

    print("Suas reservas:")
    for idx, reserva in enumerate(reservas, start=1):
        print(f"{idx}. Salão {reserva.salao} - Data: {reserva.data_reserva.strftime('%d/%m/%Y')}")

    try:
        escolha_reserva = int(input("Digite o número da reserva para excluir: "))
        if escolha_reserva < 1 or escolha_reserva > len(reservas):
            print("Erro: Escolha uma reserva válida!")
            sleep(2)
            excluir_reserva()

        reserva_escolhida = reservas[escolha_reserva - 1]
        session.delete(reserva_escolhida)
        session.commit()

        print("Reserva excluída com sucesso!")
        sleep(2)
        menu_reserva()

    except ValueError:
        print("Erro: Entrada inválida. Digite um número válido.")
        sleep(2)
        menu_reserva()

# Ver reserva
def ver_locacoes():
    os.system("cls")
    global usuario_autenticado

    if not usuario_autenticado:
        print("Você precisa estar autenticado para ver as locações.")
        sleep(2)
        return

    reservas = session.query(Reserva).filter_by(dono=usuario_autenticado.id).all()
    os.system("cls")
    if not reservas:
        print("Você não tem locações registradas.")
        input("Pressione 'ENTER' para continuar...")
        return

    print("Suas locações registradas:")
    for reserva in reservas:
        cliente = session.query(Clientes).filter_by(id=reserva.dono).first()
        os.system ("cls")

        print(f"""Salão {reserva.salao}  
Data: {reserva.data_reserva.strftime('%d/%m/%Y')}  
Cliente: {cliente.nome}""")
        input("Pressione 'ENTER' para continuar...")

    sleep(2)
    menu_reserva()

# Edita
def editar_locacoes():
    os.system("cls")
    global usuario_autenticado

    if not usuario_autenticado:
        print("Você precisa estar autenticado para editar as locações.")
        sleep(2)
        return

    reservas = session.query(Reserva).filter_by(dono=usuario_autenticado.id).all()
    if not reservas:
        os.system("cls")
        print("Você não tem reservas para editar.")
        sleep(2)
        return

    print("Suas reservas:")
    for idx, reserva in enumerate(reservas, start=1):
        print(f"{idx}. Salão {reserva.salao} - Data: {reserva.data_reserva.strftime('%d/%m/%Y')}")

    try:
        escolha_reserva = int(input("Digite o número da reserva para editar: "))
        if escolha_reserva < 1 or escolha_reserva > len(reservas):
            print("Erro: Escolha uma reserva válida!")
            sleep(2)
            return

        reserva_escolhida = reservas[escolha_reserva - 1]
        nova_data = input("Digite a nova data (DD/MM/YYYY): ")
        nova_data_obj = datetime.strptime(nova_data, "%d/%m/%Y").date()

        if nova_data_obj <= datetime.today().date():
            print("Erro: A data precisa ser no futuro!")
            sleep(2)
            return

        reserva_existente = session.query(Reserva).filter_by(salao=reserva_escolhida.salao, data_reserva=nova_data_obj).first()
        if reserva_existente:
            os.system("cls")
            print("Erro: Já existe uma reserva para esse salão nessa data!")
            sleep(2)
            return

        reserva_escolhida.data_reserva = nova_data_obj
        session.commit()

        print(f"Reserva para o Salão {reserva_escolhida.salao} foi editada para {nova_data_obj.strftime('%d/%m/%Y')}.")
        sleep(2)
        menu_reserva()

    except ValueError:
        print("Erro: Formato de data inválido! Use DD/MM/YYYY.")
        sleep(2)
        menu_reserva()

# Iniciar
def iniciar_sistema():
    while True:
        if not menu_principal():
            break

iniciar_sistema()

