package customcommon.xml.models;
import customcommon.xml.models.Nlparg;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Set;
public class Nlpword {
	private int id;
	private String cont;
	private String pos ;
	private int ne;
	private int parent;
	private String relate;
	private List<Nlparg> arg;
	public Nlpword(){
		if(arg ==null)
		arg = new ArrayList<Nlparg>();
	}
	
	public void setId(int id){
		this.id = id;
	}
	
	public void addArg(Nlparg arg){
		try{	
		if(arg !=null)
			this.arg.add(arg);
		}catch(Exception e){
			e.printStackTrace();
		}
		 
	}
	
	public void setCont(String cont){
		this.cont = cont;
	}
	
	public void setPos(String pos){
		this.pos = pos;
	}
	
	public void setNe(int ne){
		this.ne = ne;
	}
	
	public void setParent(int parent){
		this.parent = parent;
	}
	
	public void setRelate(String relate){
		this.relate = relate;
	}
	
	public int getId(){
		return this.id;
	}
	
	public String getCont(){
		return this.cont;
	}
	public String getPos(){
		return this.pos;
	}
	
	public int getNe(){
		return this.ne;
	}
	
	public int getParent(){
		return this.parent;
	}
	
	public String getRelate(){
		return this.relate;
	}
	
	public Iterator getArgs(){
		return this.arg.iterator();
	}
	
	public Nlparg findArg( int id ){
		for(Nlparg arg : this.arg){
			if(arg.getId() == id){
				return arg;
			}
		}
		return null;
	}
	
	public List<Nlparg> getArgAsList(){
		return this.arg;
	}
}
