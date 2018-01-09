package rpc.bson;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.PrintWriter;
import java.net.Socket;
import java.net.UnknownHostException;
import java.util.Map;

import net.sf.json.JSONObject;

import org.bson.BSONObject;
import org.bson.BSONEncoder;
import org.bson.BSONDecoder;
import org.bson.BasicBSONObject;
import org.bson.BasicBSONEncoder;
import org.bson.BasicBSONDecoder;

/**
 * Hello world!
 *
 */
public class App 
{
    public static void main( String[] args )
    {
        System.out.println("Demo how to write a raw Java client side according to bson-rpc protocol.");

        try {
          Socket socket = new Socket("127.0.0.1", 8181);

          OutputStream outputStream = socket.getOutputStream();
          BSONObject out = new BasicBSONObject();
          BSONEncoder encoder = new BasicBSONEncoder();
          out.put("fn", "__stats__");
          byte[] bin = encoder.encode(out);
          outputStream.write(bin);
          outputStream.flush();

          InputStream inputStream = socket.getInputStream();
          BSONDecoder decoder = new BasicBSONDecoder();
          BSONObject in = decoder.readObject(inputStream); // read exactly a single BSON Object

          Map m = in.toMap();
          JSONObject json = JSONObject.fromObject(m);
          System.out.println(json.toString());

          // to keep the persisten connection, don't close them
          //outputStream.close(); 
          //inputStream.close();
          //socket.close();
        } catch (UnknownHostException e) {
          e.printStackTrace();
        } catch (IOException e) {
          e.printStackTrace();
        }

    }
}
