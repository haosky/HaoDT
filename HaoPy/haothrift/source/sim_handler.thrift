namespace java gxthrift.simhandler
namespace py  gxthrift.simhandler

service sim_query{
    string sim_unit_query(1:string _uuid)
    string sim_user_query(1:string _uuid)
    string sim_project_query(1:string _uuid)
    string keyword_query(1:string _uuid,2:i16 num)
    string topic_query(1:string _uuid)
    string entry_word_query(1:string _uuid)
    string new_word_query(1:string _uuid)
    string relation_query(1:string _uuid)
    string common_query_api(1:string jsonparams)
}

service sim_develop{
    string get_art_sim(1:string art_content)
    string get_difference2arts(1:string artsrc,2:string artdsc)
    string get_differencelist()
    string get_differenceinfo(1:string docid)
    string get_differenceparse(1:string docid)
    string get_differencecomment(1:string docid)
    string get_same_list(1:string input)
    string get_different_2_docid(1:string left_id,2:string right_id)
    string get_doc_same_all(1:string docid,2:string suuid)
}

service rest_develop{
    string get_entry_relative(1:string uuid,2:i32 num)
    string get_relative_list(1:string search_str)
}