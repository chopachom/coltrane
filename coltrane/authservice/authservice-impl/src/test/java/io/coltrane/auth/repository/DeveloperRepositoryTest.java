package io.coltrane.auth.repository;

import io.coltrane.auth.domain.Developer;
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
@ContextConfiguration("/spring/repositories-test-context.xml")
@Transactional
public class DeveloperRepositoryTest {

    @Autowired
    private DeveloperRepository developerRepository;
    
    @Test
    public void testCreateAndRead() {
        Developer developer = DomainHelper.createDeveloper();
        developerRepository.save(developer);
        assertNotNull(developer.getId());
        Developer savedDeveloper = developerRepository.findOne(developer.getId());
        assertEquals(developer, savedDeveloper);
    }
    
    @Test
    public void testDelete() {
        Developer developer = DomainHelper.createDeveloper();
        developerRepository.save(developer);
        developerRepository.delete(developer.getId());
        assertNull(developerRepository.findOne(developer.getId()));
    }
}
