package io.coltrane.auth.repository;

import io.coltrane.auth.domain.Application;
import io.coltrane.auth.domain.Developer;
import io.coltrane.auth.domain.FacebookUser;

/**
 *
 * @author nik
 */
public class DomainHelper {

    public static Developer createDeveloper() {
        Developer developer = new Developer();
        developer.setAuthHash("123");
        developer.setEmail("test@mail.com");
        developer.setFirstName("Firstname");
        developer.setLastName("Lastname");
        developer.setNickName("Nickname");
        developer.setPasswordHash("123321123");
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
        user.setPasswordHash("12321323");
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
}
