package hbasemodels;

import java.io.Serializable;
import java.security.NoSuchAlgorithmException;

/**
 * Created by gxkj-941 on 2017/4/6.
 */
public abstract  class BaseOP implements Serializable {
    public abstract byte[] getRowKey() throws NoSuchAlgorithmException;
}
