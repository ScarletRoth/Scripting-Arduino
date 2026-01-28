import tempfile
import os

def main():
    with tempfile.NamedTemporaryFile(
        mode='w+',
        encoding='utf-8',
        delete=False
    ) as temp_file:
        temp_file.write("Bonjour \n Ceci est un fichier temporaire.\n")
        temp_file.seek(0)
        print("\n--- Contenu du fichier temporaire ---")
        print(temp_file.read())
        temp_filename = os.path.abspath(temp_file.name)

    print("\n Chemin exact du fichier temporaire :")
    print(temp_filename)
    
    while True:
        print("\n Que voulez-vous faire ?")
        print("1 - Supprimer le fichier temporaire")
        print("2 - Conserver le fichier temporaire")
        choice = input("Votre choix (1 ou 2) : ").strip()
        if choice == "1":
            os.remove(temp_filename)
            print("\n Fichier supprimé")
            break
        elif choice == "2":
            print("\n Fichier conservé")
            print("Vous pouvez l’ouvrir directement avec ce chemin.")
            break
        else:
            print("\n Choix invalide, veuillez réessayer.")
if __name__ == "__main__":
    main()
