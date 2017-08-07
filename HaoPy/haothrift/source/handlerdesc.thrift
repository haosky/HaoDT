namespace java gxthrift.mlhandler
namespace py  gxthrift.mlhandler

service query2artsame{
    string artcomp(1:string article_src,2:string article_dst)
}