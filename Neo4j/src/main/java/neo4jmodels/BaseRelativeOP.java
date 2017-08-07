package neo4jmodels;

import java.io.Serializable;

/**
 * Created by gxkj-941 on 2017/4/6.
 */
public abstract class BaseRelativeOP implements Serializable {
    public abstract String makeCypher(Object...params);

}
