def get_urls_file(file_path):
    from etlqs.ambassador import get_from_raw_store
        
    return get_from_raw_store(bucket='urlsraw', file_path=file_path)

def load_urls_file(destination_path):
    from etlqs.ambassador import put_to_raw_store
    
    put_to_raw_store(bucket='urlsraw', file_path=destination_path)

def extract_urls_file(file_name):
    """
    return urls_file in the raw store
    """
    from etlqs.ambassador import get_from_raw_store
        
    return get_from_raw_store(bucket='urls', file_path=file_name)


def get_metas(file_name):
    """
    Get informations remotely from the raw store
    informations are size, type and last modified
    """
    from etlqs.ambassador import find_by_name_from_raw_store
    
    return find_by_name_from_raw_store(bucket='urls', file_name=file_name)


