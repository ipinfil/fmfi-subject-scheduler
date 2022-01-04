from config import students_db_path
import os

class System:
    @staticmethod
    def get_students_db_path(name:str):
        return students_db_path + name + '.txt'

    @staticmethod
    def handle_login(name: str) -> bool:
        path = System.get_students_db_path(name)

        if not os.path.exists(path):
            open(path, 'x').close()

        with open(path, 'r+') as f:
            content = f.read()

        return content

class PredicateManager:
    PREDMET = 1
    UCITEL = 2
    TECHNOLOGIA = 3
    TEMATICKY_OKRUH = 4
    STUDENT_TECHNOLOGIA = 5
    STUDENT_TEMATICKY_OKRUH = 6
    STUDENT_VYLUCENY_UCITEL = 7
    STUDENT_ZAPISANY_PREDMET = 8
    ODPORUCENY_PREDMET = 9
    NEZAPISANY_PREDMET = 10
    CHYBA_ZAPISANA_PREREKVIZITA = 11

    PREDICATES = {
        PREDMET : {
            'title' : 'Predmety',
            'name' : 'predmet',
            'arity' : 6,
            'arguments' : {
                'id' : 'ID',
                'name' : 'Meno',
                'year' : 'Odp. rok',
                'semester' : 'Semester',
                'credits' : 'Kredity',
                'block_id' : 'Blok ID'
            }
        },
        UCITEL : {
            'title': 'Učitelia',
            'name' : 'ucitel',
            'arity' : 2,
            'arguments' : {
                'id' : 'ID',
                'name' : 'Meno'
            }
        },
        TECHNOLOGIA : {
            'title' : 'Technológie',
            'name' : 'technologia',
            'arity' : 2,
            'arguments' : {
                'id' : 'ID',
                'name' : 'Meno'
            }
        },
        TEMATICKY_OKRUH : {
            'title' : 'Tématické okruhy',
            'name' : 'tematicky_okruh',
            'arity' : 2,
            'arguments' : {
                'id' : 'ID',
                'name' : 'Meno'
            }
        },
        STUDENT_TECHNOLOGIA : {
            'title' : 'Obmedzujúca technológia študenta',
            'name' : 'student_technologia',
            'arity' : 1,
            'arguments' : {
                'id_technologia' : 'ID Technológie'
            }
        },
        STUDENT_TEMATICKY_OKRUH : {
            'title' : 'Obmedzujúci tématický okruh študenta',
            'name' : 'student_tematicky_okruh',
            'arity' : 1,
            'arguments' : {
                'id_tematicky_okruh' : 'ID Tématického okruhu'
            }
        },
        STUDENT_VYLUCENY_UCITEL : {
            'title' : 'Vylúčení učitelia',
            'name' : 'student_vyluceny_ucitel',
            'arity' : 1,
            'arguments' : {
                'id_ucitel' : 'ID Učiteľa'
            }
        },
        STUDENT_ZAPISANY_PREDMET : {
            'title' : 'Zapísané predmety',
            'name' : 'student_zapisany_predmet',
            'arity' : 2,
            'arguments' : {
                'id_predmet' : 'ID Predmetu',
                'name' : 'Názov predmetu',
                'rok' : 'Rok štúdia',
                'semester' : 'Semester'
            }
        },
        ODPORUCENY_PREDMET : {
            'title' : 'Odporučené predmety',
            'name' : 'odporuceny_predmet',
            'arity' : 4,
            'arguments' : {
                'id_predmet' : 'ID Predmetu',
                'name' : 'Názov predmetu',
                'semester' : 'Semester',
                'prerequisite' : 'Prerekvizita'
            }
        },
        NEZAPISANY_PREDMET : {
            'title' : 'Nezapísané predmety',
            'name' : 'nezapisany_predmet',
            'arity' : '3',
            'arguments' : {
                'id_predmet' : 'ID Predmetu',
                'name' : 'Názov predmetu',
                'semester' : 'Semester'
            }
        },
        CHYBA_ZAPISANA_PREREKVIZITA : {
            'title' : 'Chýbajúce prerekvizity',
            'name' : 'chyba_zapisana_prerekvizita',
            'arity' : '4',
            'arguments' : {
                'id_predmet' : 'ID Predmetu',
                'predmet_name' : 'Názov predmetu',
                'id_prerekvizita' : 'ID Prerekvizita',
                'prerekvizita_name' : 'Názov prerekvizity'
            }
        }
    }

    SUMMER_SEMESTER_CONST = 'l'
    WINTER_SEMESTER_CONST = 'z'

    @classmethod
    def _get_predicate(cls, predicate: int):
        if not cls.PREDICATES.get(predicate, False):
            raise ValueError('No such predicate exists.')

        return cls.PREDICATES.get(predicate)

    @classmethod
    def get_predicate_name(cls, predicate: int):
        return cls._get_predicate(predicate)['name']

    @classmethod
    def get_predicate_title(cls, predicate: int):
        return cls._get_predicate(predicate)['title']

    @classmethod
    def get_predicate_argument_titles(cls, predicate: int):
        return cls._get_predicate(predicate)['arguments'].values()