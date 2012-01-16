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
import org.springframework.transaction.annotation.Transactional;

import static org.junit.Assert.*;
/**
 *
 * @author nik
 */
@RunWith(SpringJUnit4ClassRunner.class)
@ContextConfiguration("/spring/repositories-context.xml")
@Transactional
public class FacebookUserRepositoryTest {
    
    @Autowired
    private FacebookUserRepository repository;
    
    @Test
    public void testCreateAndRead() {
        FacebookUser user = createFacebookUser();
        repository.save(user);
        assertNotNull(user.getId());
        FacebookUser actualUser = repository.findOne(user.getId());
        assertEquals(user, actualUser);
    }
    
    @Test
    public void testDelete() {
        FacebookUser user = createFacebookUser();
        repository.save(user);
        repository.delete(user.getId());
        assertNull(repository.findOne(user.getId()));
    }

    private FacebookUser createFacebookUser() {
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
}
