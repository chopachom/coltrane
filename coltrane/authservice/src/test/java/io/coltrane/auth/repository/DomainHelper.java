package io.coltrane.auth.repository;

import io.coltrane.auth.domain.Application;
import io.coltrane.auth.domain.Developer;
import io.coltrane.auth.domain.FacebookUser;
import org.mindrot.jbcrypt.BCrypt;

/**
 *
 * @author nik
 */
public class DomainHelper {

    public static Developer createDeveloper() {
        return createDeveloper("123321123");
    }
    
    public static Developer createDeveloper(String pwd) {
        Developer developer = new Developer();
        developer.setAuthHash("123");
        developer.setEmail("test@mail.com");
        developer.setFirstName("Firstname");
        developer.setLastName("Lastname");
        developer.setNickName("Nickname");
        developer.setPasswordHash(hashPwd(pwd));
        developer.setToken("333444");
        return developer;
    }
    
    public static FacebookUser createFacebookUser() {
        FacebookUser user = new FacebookUser();
        user.setAccessToken("123");
        user.setAuthHash("321");
        user.setEmail("test@mail.com");
        user.setFacebookId(123L);
        user.setFirstName("Firstname");
        user.setLastName("Lastname");
        user.setNickName("Nickname");
        user.setPasswordHash(hashPwd("12321323"));
        user.setToken("111");
        return user;
    }
    
    public static Application createApplication(String domain) {
        Application app = new Application();
        app.setAppDomain(domain);
        app.setDescription("App description");
        app.setName(domain);
        return app;
    }
    
    public static String hashPwd(String pwd) {
        return BCrypt.hashpw(pwd, BCrypt.gensalt());
    }
}
