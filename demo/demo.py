from SPARQLWrapper import SPARQLWrapper, CSV, POST

# RDFox SPARQL 엔드포인트 설정
sparql = SPARQLWrapper("http://localhost:12110/datastores/headache/sparql")

prefixes = """
    PREFIX g: <http://joyhong.tistory.com/graph/>
    PREFIX zig: <http://joyhong.tistory.com/zigzag/>
"""

def run_query(query_string:str):
    sparql.setQuery(prefixes+query_string)
    sparql.setMethod(POST)
    # 반환 형식 설정 (JSON)
    sparql.setReturnFormat(CSV)
    # 쿼리 실행 및 결과 받기
    results = sparql.query().convert()
    return results.decode('utf-8')


def check_patient():
    query = """
    SELECT *
    FROM g:user
    FROM g:inferred
    WHERE {
        ?s a ont:Patient.
        ?s ?p ?o.
    }
    """
    print(run_query(query))


def check_patient_with_status_results():
    query = """
    SELECT *
    FROM g:user
    FROM g:inferred
    WHERE {
        ?s a ont:Patient.
        ?s ont:hasStatus ?status.
        ?s ont:hasResult ?result.
        OPTIONAL{ ?status ?sp ?so. }
        OPTIONAL{ ?result ?rp ?ro. }
    }
    """
    print(run_query(query))


def user_setup():
    query = """
        INSERT DATA {
            graph g:user{
                zig:P01 a ont:Patient.
                zig:P01 ont:hasStatus zig:PC_P01 .
                zig:P01 ont:hasResult zig:DC_P01 .
            }
        }
        """
    print(run_query(query))


def start_examination_1():
    query = """
        INSERT DATA {
            graph g:user{
                zig:P01 ont:hasSymptoms zig:중증도_심도_통증 , zig:구토 , zig:빛공포증 , zig:박동양상 , zig:편측위치 .
            }
        }
        """
    print(run_query(query))


def add_duration():
    query = """
        INSERT DATA {
            graph g:user{
                zig:P01 ont:duration 3.
            }
        }
        """
    print(run_query(query))


def update_duration(duration):
    query = """
        DELETE  {
            graph g:user{
                zig:P01 ont:duration ?d.
            }
        }
        INSERT  {
            graph g:user{
                zig:P01 ont:duration %s.
            }
        }
        WHERE {
            graph g:user{
                zig:P01 ont:duration ?d.
            }
        }

        """ % duration
    print(run_query(query))

def add_frequency():
    query = """
        INSERT DATA {
            graph g:user{
                zig:P01 ont:frequency 3.
            }
        }
        """
    print(run_query(query))

def update_frequency(frequency):
    query = """
        DELETE  {
            graph g:user{
                zig:P01 ont:frequency ?d.
            }
        }
        INSERT  {
            graph g:user{
                zig:P01 ont:frequency %s.
            }
        }
        WHERE {
            graph g:user{
                zig:P01 ont:frequency ?d.
            }
        }

        """ % frequency
    print(run_query(query))



# check_patient()
# user_setup()
# check_patient_with_status_results()
# start_examination_1()
# check_patient_with_status_results()
# add_duration() # 3시간
# check_patient_with_status_results()
# update_duration(8) #8시간
# check_patient_with_status_results()
# add_frequency() #3번
# check_patient_with_status_results()
update_frequency(5) #5번
check_patient_with_status_results()