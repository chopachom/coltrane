package io.coltrane.auth;

import io.coltrane.auth.server.Server;
import org.springframework.context.support.ClassPathXmlApplicationContext;

/**
 * App's main class
 * @author nik
 */
public class App {

    public static void main(String[] args) {
        ClassPathXmlApplicationContext context = new ClassPathXmlApplicationContext("/spring/spring-context.xml");
        Server server = (Server) context.getBean("thriftServer");
        server.start();
    }
}
