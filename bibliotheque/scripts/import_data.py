from bibliothèque.models import Categorie
def run():
    for i in range( 5,15):
        categorie=Categorie()
        categorie.nom="Categorie N° #%d" % i
        categorie.nombre_livre="Nombre de livres N° #%d " % i
        categorie.image="http://default"
        categorie.save()
print("Opération réussie")
        