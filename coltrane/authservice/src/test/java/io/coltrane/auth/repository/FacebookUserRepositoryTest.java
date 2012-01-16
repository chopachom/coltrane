/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package io.coltrane.auth.repository;

import io.coltrane.auth.domain.FacebookUser;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringJUnit4ClassRunner;

import static org.junit.Assert.assertNotNull;
/**
 *
 * @author nik
 */
@RunWith(SpringJUnit4ClassRunner.class)
@ContextConfiguration("/spring/repositories-context.xml")
public class FacebookUserRepositoryTest {
    
    @Autowired
    private FacebookUserRepository repository;
    
    @Test
    public void testCreateAndRead() {
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
        
        FacebookUser savedUser = repository.save(user);
        assertNotNull(savedUser.getId());
    }
}
