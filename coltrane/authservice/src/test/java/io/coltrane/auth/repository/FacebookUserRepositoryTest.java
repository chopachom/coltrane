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
        FacebookUser user = DomainHelper.createFacebookUser();
        repository.save(user);
        assertNotNull(user.getId());
        FacebookUser actualUser = repository.findOne(user.getId());
        assertEquals(user, actualUser);
    }
    
    @Test
    public void testDelete() {
        FacebookUser user = DomainHelper.createFacebookUser();
        repository.save(user);
        repository.delete(user.getId());
        assertNull(repository.findOne(user.getId()));
    }
}
