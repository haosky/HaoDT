package util;

import com.cybermkd.mongo.plugin.MongoPlugin;
import com.mongodb.MongoClient;

public class MongoUtil {

	public static MongoClient getMongoClient() {
		MongoPlugin plugin = new MongoPlugin();
		plugin.add("127.0.0.1", 27020).add("127.0.0.1", 27021).add("127.0.0.1", 27022);
		plugin.setDatabase("admin");
		plugin.auth("admin", "tingting");
		plugin.setDebug(false);

		return plugin.getMongoClient();
	}

	public static MongoClient getMongoClient(boolean isDebug) {
		MongoPlugin plugin = new MongoPlugin();
		plugin.add("127.0.0.1", 27020).add("127.0.0.1", 27021).add("127.0.0.1", 27022);
		plugin.setDatabase("admin");
		plugin.auth("admin", "tingting");
		plugin.setDebug(isDebug);

		return plugin.getMongoClient();
	}

}
