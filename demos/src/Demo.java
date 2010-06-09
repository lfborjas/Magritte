import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.io.IOException;
import java.io.InputStream;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import com.google.gson.Gson;
public class Demo {
	public static String getContents(InputStream s) throws IOException{
				BufferedReader in = new BufferedReader(new InputStreamReader(s));
				String inputLine;
				StringBuffer outLine = new StringBuffer();
				while ((inputLine = in.readLine()) != null)
				    outLine.append(inputLine);
				in.close();
				return outLine.toString();
	}
	
	public static void main(String[] args) throws IOException, MalformedURLException {
		//build the request
		URL serviceCall = null;		
		String call =  "http://localhost:8000/api/getRecommendations/";
		String appId = "0a0c8647baf451dc081429aa9815d476";
		String appUser = "testUser";
		String context = "Science!"; //remember to url-encode
		String urlpath = String.format("%s?appId=%s&appUser=%s&content=%s", call, appId, appUser, context);
		serviceCall = new URL(urlpath);				
		//get the response:
		HttpURLConnection conn = (HttpURLConnection)serviceCall.openConnection();		
		//interpret the response:
		InputStream is;		
		if(conn.getResponseCode() < 400){
			is = conn.getInputStream();			
			Gson gson = new Gson();
			String json = getContents(is);			
			Result result = gson.fromJson(json, Result.class);			
			System.out.println("Recommendations");
			for(Doc r: result.results){
				System.out.printf("Title: %s, URL: %s \n", r.title, r.url);
			}
		}else{
			System.out.printf("Error in call: %s", conn.getErrorStream().toString());
		}
	}
}
