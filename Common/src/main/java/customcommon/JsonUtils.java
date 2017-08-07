package customcommon;

import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.JSONValue;
import java.util.Map;
import java.util.List;

public class JsonUtils {
	
	public static JSONArray toJSON(String str){
		return (JSONArray) JSONValue.parse(str);
	
	}

 	public static String mapToJSON(Map map){		
		return JSONObject.toJSONString(map);
		}
	
 	public static String ListToJson(List list){
 		return JSONArray.toJSONString(list);
 	}
}
