package customcommon;
import java.lang.reflect.Method;
import java.lang.reflect.Field;
import java.lang.reflect.InvocationTargetException;
/**
 * Created by gxkj-941 on 2017/4/6.
 */
public class BeanEval<T> {
    public BeanEval(){

    }

    public Object getEntry(T object,String entryName) throws  NoSuchMethodException,IllegalAccessException,InvocationTargetException,SecurityException{
        Method setAttributeMethod = null;
        if(entryName.startsWith("get")) {
            setAttributeMethod = object.getClass().getDeclaredMethod(entryName);
           return setAttributeMethod.invoke(object);
        }
        throw new NoSuchMethodException("only use as get method");
    }

    public void setEntry(T object,String entryName,Object entryValue) throws  NoSuchMethodException,IllegalAccessException,InvocationTargetException,SecurityException{
        Method setAttributeMethod = null;
        if(entryName.startsWith("get")) {
            setAttributeMethod = object.getClass().getDeclaredMethod(entryName);
            setAttributeMethod.invoke(object,entryValue);
        }
        throw new NoSuchMethodException("only use as set method");
    }

    public Field[] getEntryFields(T object){
        Field[] field = object.getClass().getDeclaredFields();
        return field;
    }

}
