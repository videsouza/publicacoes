import requests


BASE_URL = "https://oracleapex.com/ords/videsouza/grade"


def buscar(endpoint):
    url = f"{BASE_URL}/{endpoint}"

    resposta = requests.get(url, timeout=30)
    resposta.raise_for_status()

    dados = resposta.json()

    return dados["items"]


def main():
    aulas = buscar("aulas")
    horarios = buscar("horarios")
    disponibilidades = buscar("disponibilidades")
    salas = buscar("salas")

    print("\n=== AULAS ===")
    for item in aulas:
        print(item)

    print("\n=== HORÁRIOS ===")
    for item in horarios:
        print(item)

    print("\n=== DISPONIBILIDADES ===")
    for item in disponibilidades:
        print(item)

    print("\n=== SALAS ===")
    for item in salas:
        print(item)


if __name__ == "__main__":
    main()