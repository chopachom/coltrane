package io.coltrane.auth.repository;

import io.coltrane.auth.domain.Application;
import io.coltrane.auth.domain.Developer;
import java.util.Arrays;
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
public class ApplicationRepositoryTest {

    @Autowired
    private DeveloperRepository developerRepository;
    
    @Autowired
    private ApplicationRepository appRepository;
    
    @Test
    public void testCreateAndRead() {
        Developer developer = DomainHelper.createDeveloper();
        Application app1 = DomainHelper.createApplication("app1");
        app1.setAuthor(developer);
        Application app2 = DomainHelper.createApplication("app2");
        app2.setAuthor(developer);
        developer.setApplications(Arrays.asList(app1 ,app2));
        
        developerRepository.save(developer);
        appRepository.save(app1);
        assertNotNull(app1.getId());
        appRepository.save(app2);
        assertNotNull(app2.getId());
        
        Application savedApp1 = appRepository.findOne(app1.getId());
        Application savedApp2 = appRepository.findOne(app2.getId());
        assertEquals(developer, savedApp1.getAuthor());
        assertEquals(developer, savedApp2.getAuthor());
        
        Developer savedDeveloper = developerRepository.findOne(developer.getId());
        assertEquals(Arrays.asList(app1, app2), savedDeveloper.getApplications());
    }
    
    @Test
    public void testDelete() {
        Developer developer = DomainHelper.createDeveloper();
        Application app1 = DomainHelper.createApplication("app1");
        app1.setAuthor(developer);
        developerRepository.save(developer);
        appRepository.save(app1);
        appRepository.delete(app1.getId());
        assertNull(appRepository.findOne(app1.getId()));
    }
}
