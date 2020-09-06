from ..kernel import core
from ..kernel.core import VSkillModifier as V
from ..character import characterKernel as ck
from functools import partial
from ..status.ability import Ability_tool
from ..execution.rules import RuleSet, InactiveRule
from . import globalSkill
from .jobbranch import warriors
from math import ceil

######   Passive Skill   ######
class MorphGaugeWrapper(core.StackSkillWrapper):
    def __init__(self, skill, final_figuration):
        super(MorphGaugeWrapper, self).__init__(skill, 700)
        self.set_name_style("+%d")
        self.final_figuration = final_figuration
        
    def vary(self, d):
        if self.final_figuration.is_not_active() or d<0:
            return super(MorphGaugeWrapper, self).vary(d)
        else:
            return core.ResultObject(0, core.CharacterModifier(), 0, 0, sname = self._id, spec = 'graph control')

    def get_modifier(self): # 아이언 윌 - 모프 게이지 단계당 데미지 3% 증가
        if self.final_figuration.is_active() or self.stack >= 700: # 3단계
            return core.CharacterModifier(pdamage = 9)
        if self.stack >= 300: # 2단계
            return core.CharacterModifier(pdamage = 6)
        if self.stack >= 100: # 1단계
            return core.CharacterModifier(pdamage = 3)
        return core.CharacterModifier()

class JobGenerator(ck.JobGenerator):
    def __init__(self):
        super(JobGenerator, self).__init__()
        self.vSkillNum = 5
        self.vEnhanceNum = 13
        self.jobtype = "str"
        self.jobname = "카이저"
        self.ability_list = Ability_tool.get_ability_set('boss_pdamage', 'crit', 'buff_rem')
        self.preEmptiveSkills = 1
        self._combat = 0

    def get_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule(InactiveRule('인퍼널 브레스', '파이널 피규레이션'), RuleSet.BASE)
        ruleset.add_rule(InactiveRule('마제스티 오브 카이저', '파이널 피규레이션'), RuleSet.BASE)
        return ruleset
        
    def get_passive_skill_list(self, vEhc, chtr : ck.AbstractCharacter):
        passive_level = chtr.get_base_modifier().passive_level + self._combat

        InnerBlaze = core.InformedCharacterModifier("이너 블레이즈",stat_main = 20)
        AdvancedInnerBlaze = core.InformedCharacterModifier("어드밴스드 이너 블레이즈",stat_main = 30)
        Catalyze = core.InformedCharacterModifier("카탈라이즈", patt=30, crit=20, pdamage_indep=20)
        AdvancedWillOfSwordPassive = core.InformedCharacterModifier("어드밴스드 윌 오브 소드(패시브)",att = 20 + 2*ceil(passive_level/3))
        UnflinchingCourage = core.InformedCharacterModifier("언플린칭 커리지",armor_ignore = 40 + passive_level)
        AdvancedSwordMastery = core.InformedCharacterModifier("어드밴스드 소드 마스터리", att = 30 + passive_level, crit_damage = 15 + passive_level//3, crit=20 + passive_level//2)
    
        return [InnerBlaze, AdvancedInnerBlaze, Catalyze, 
                AdvancedWillOfSwordPassive, UnflinchingCourage, AdvancedSwordMastery]
                
    def get_not_implied_skill_list(self, vEhc, chtr : ck.AbstractCharacter):
        passive_level = chtr.get_base_modifier().passive_level + self._combat

        WeaponConstant = core.InformedCharacterModifier("무기상수",pdamage_indep = 34)
        Mastery = core.InformedCharacterModifier("숙련도",pdamage_indep = -5 + 0.5*ceil(passive_level / 2))
        
        ReshuffleSwitchAttack = core.InformedCharacterModifier("리셔플스위치:공격",att = 45, crit = 20, boss_pdamage = 18)
        
        return [WeaponConstant, Mastery, ReshuffleSwitchAttack]
        
    def generate(self, vEhc, chtr : ck.AbstractCharacter, combat : bool = False):
        '''
        모프 수급량
        어윌소 12*5
        프로미넌스 50
        인퍼널 40
        기가슬래셔 5
        윙비트 공격당 1
        
        하이퍼
        기가 슬래셔-리인포스, 보너스 어택
        윙비트-리인포스, 퍼시스트, 엑스트라 어택
        
        코어 강화 우선순위
        기가 슬래셔-윙비트-소드 스트라이크-윌 오브 소드-인퍼널 브레스-페트리파이드-프로미넌스
        '''

        passive_level = chtr.get_base_modifier().passive_level + self._combat
        # Buff skills
        RegainStrenth = core.BuffSkill("리게인 스트렝스", 0, 240000, rem = True, pdamage_indep = 15).wrap(core.BuffSkillWrapper)
        BlazeUp = core.BuffSkill("블레이즈 업", 0, 240000, att = 20, rem = True).wrap(core.BuffSkillWrapper)
        SoulContract = globalSkill.soul_contract()
    
        FinalFiguration = core.BuffSkill("파이널 피규레이션", 0, 60000, pdamage_indep = 15, boss_pdamage = 10, rem = True).wrap(core.BuffSkillWrapper)
        MorphGauge = MorphGaugeWrapper(core.BuffSkill("모프 게이지", 0, 9999999), FinalFiguration)

        Wingbit_Delay = core.DamageSkill("윙비트(딜레이)", 360, 0, 0).wrap(core.DamageSkillWrapper)
        Wingbit_Delay_Fig = core.DamageSkill("윙비트(딜레이)(변신)", 540, 0, 0).wrap(core.DamageSkillWrapper)
        Wingbit_1 = core.SummonSkill("윙비트", 0, 330, 200, 1, 15900, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 1, 3, True).wrap(core.SummonSkillWrapper)  #48타
        Wingbit_2 = core.SummonSkill("윙비트(2)", 0, 330, 200, 1, 15900, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 1, 3, True).wrap(core.SummonSkillWrapper)  #48타
        
        GigaSlasher = core.DamageSkill("기가 슬래셔", 540, 330 + 2*self._combat, 9+1, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
        GigaSlasher_Fig = core.DamageSkill("기가 슬래셔(변신)", 540, 330+2*self._combat, 11+1, modifier = core.CharacterModifier(pdamage = 20)).setV(vEhc, 0, 2, False).wrap(core.DamageSkillWrapper)
    
        AdvancedWillOfSword_Dummy = core.DamageSkill("어드밴스드 윌 오브 소드(시전)", 0, 0, 0, cooltime = 10000, red=True).wrap(core.DamageSkillWrapper)
        AdvancedWillOfSword = core.DamageSkill("어드밴스드 윌 오브 소드", 150, 400+3*passive_level, 4*5, cooltime = -1).setV(vEhc, 3, 2, True).wrap(core.DamageSkillWrapper)
        AdvancedWillOfSword_Fig = core.DamageSkill("어드밴스드 윌 오브 소드(변신)", 600, 400+3*passive_level, (4+1)*5, cooltime = -1).setV(vEhc, 3, 2, True).wrap(core.DamageSkillWrapper)

        InfernalBreath = core.DamageSkill("인퍼널 브레스", 780, 300 + 4*self._combat, 8, cooltime = (20-self._combat)*1000, red=True).setV(vEhc, 4, 2, True).wrap(core.DamageSkillWrapper)
        InfernalBreath_Tile = core.SummonSkill("인퍼널 브레스(바닥)", 0, 1200, 200 + 3*self._combat, 2, 20000, cooltime = -1).setV(vEhc, 4, 2, True).wrap(core.SummonSkillWrapper)

        Petrified = core.SummonSkill("페트리파이드", 450, 3030, 400, 1, 60000).setV(vEhc, 5, 2, False).wrap(core.SummonSkillWrapper)
    
        # 하이퍼
        MajestyOfKaiser = core.BuffSkill("마제스티 오브 카이저", 900, 30000, att = 30, cooltime = 90000).wrap(core.BuffSkillWrapper)
        FinalTrance = core.BuffSkill("파이널 트랜스", 0, 60000, cooltime = 300000).wrap(core.BuffSkillWrapper) # 딜레이 모름

        Prominence_Dummy = core.DamageSkill("프로미넌스(시전)", 0, 0, 0, cooltime = 60000).wrap(core.DamageSkillWrapper)
        Prominence = core.DamageSkill("프로미넌스", 2220, 1000, 15, cooltime = -1).setV(vEhc, 6, 2, True).wrap(core.DamageSkillWrapper)
        Prominence_Fig = core.DamageSkill("프로미넌스(변신)", 1530, 1000, 15, cooltime = -1).setV(vEhc, 6, 2, True).wrap(core.DamageSkillWrapper)

        # 5차
        Phanteon = core.DamageSkill("판테온", 420, 2000+80*vEhc.getV(4,4), 10, cooltime = 1200*1000, red=True).isV(vEhc,4,4).wrap(core.DamageSkillWrapper)

        GuardianOfNova_1 = core.SummonSkill("가디언 오브 노바(1)", 600, 45000/46, 450+15*vEhc.getV(2,2), 4, (30+int(0.5*vEhc.getV(2,2)))*1000, cooltime = 120000, red=True).isV(vEhc,2,2).wrap(core.SummonSkillWrapper) # 46*4타
        GuardianOfNova_2 = core.SummonSkill("가디언 오브 노바(2)", 0, 45000/34, 250+10*vEhc.getV(2,2), 6, (30+int(0.5*vEhc.getV(2,2)))*1000, cooltime = -1).isV(vEhc,2,2).wrap(core.SummonSkillWrapper) # 34*6타
        GuardianOfNova_3 = core.SummonSkill("가디언 오브 노바(3)", 0, 45000/26, 900+35*vEhc.getV(2,2), 2, (30+int(0.5*vEhc.getV(2,2)))*1000, cooltime = -1).isV(vEhc,2,2).wrap(core.SummonSkillWrapper) # 26*2타
    
        # 윌 오브 소드: 스트라이크는 소환, 시전 2회 모두 액션 딜레이가 적용됨. 일반 150ms 변신 600ms
        WillOfSwordStrike_Dummy = core.DamageSkill("윌 오브 소드: 스트라이크(시전)", 0, 0, 0, cooltime = 30000, red=True).isV(vEhc,3,3).wrap(core.DamageSkillWrapper)
        WillOfSwordStrike = core.DamageSkill("윌 오브 소드: 스트라이크", 150*2, 500+20*vEhc.getV(3,3), 4*5).isV(vEhc,3,3).wrap(core.DamageSkillWrapper)
        WillOfSwordStrike_Explode = core.DamageSkill("윌 오브 소드: 스트라이크(폭발)", 0, 1000+40*vEhc.getV(3,3), 6*5).isV(vEhc,3,3).wrap(core.DamageSkillWrapper)
        WillOfSwordStrike_Fig = core.DamageSkill("윌 오브 소드: 스트라이크(변신)", 600*2, 500+20*vEhc.getV(3,3), (4+1)*5).isV(vEhc,3,3).wrap(core.DamageSkillWrapper)
        WillOfSwordStrike_Fig_Explode = core.DamageSkill("윌 오브 소드: 스트라이크(폭발)(변신)", 0, 1000+40*vEhc.getV(3,3), (6+1)*5).isV(vEhc,3,3).wrap(core.DamageSkillWrapper)  
        
        DrakeSlasher_Dummy = core.DamageSkill("드라코 슬래셔(시전)", 540, 0, 0, cooltime = (7-(vEhc.getV(0,0)//15))*1000, red=True).wrap(core.DamageSkillWrapper)
        DrakeSlasher = core.DamageSkill("드라코 슬래셔", 0, 500+5*vEhc.getV(0,0), 10+1, modifier = core.CharacterModifier(crit=100, armor_ignore=50) + core.CharacterModifier(pdamage = 20)).setV(vEhc, 0, 2, False).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        DrakeSlasher_Projectile = core.DamageSkill("드라코 슬래셔(발사)", 0, 500+5*vEhc.getV(0,0), 6+1, modifier = core.CharacterModifier(crit=100, armor_ignore=50) + core.CharacterModifier(pdamage = 20)).setV(vEhc, 0, 2, False).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        DrakeSlasher_Fig = core.DamageSkill("드라코 슬래셔(변신)", 0, 500+5*vEhc.getV(0,0), 10+2+1, modifier = core.CharacterModifier(crit=100, armor_ignore=50) + core.CharacterModifier(pdamage = 20)).setV(vEhc, 0, 2, False).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        DrakeSlasher_Fig_Projectile = core.DamageSkill("드라코 슬래셔(발사)(변신)", 0, 500+5*vEhc.getV(0,0), 6+2+1, modifier = core.CharacterModifier(crit=100, armor_ignore=50) + core.CharacterModifier(pdamage = 20)).setV(vEhc, 0, 2, False).isV(vEhc,0,0).wrap(core.DamageSkillWrapper)
        
        ######   Skill Wrapper   ######
        
        # 파이널 피규레이션
        FinalFiguration.onAfter(MorphGauge.stackController(-9999, name = "게이지 리셋"))
        FinalFiguration.onConstraint(core.ConstraintElement("게이지 충전시 변신", MorphGauge, partial(MorphGauge.judge, 700, 1)))

        # 파이널 트랜스
        FinalTrance.onAfter(FinalFiguration.controller(60000, "set_enabled_and_time_left"))
        FinalTrance.onConstraint(core.ConstraintElement("파이널 피규레이션 여부 확인", FinalFiguration, FinalFiguration.is_not_active))
        
        # 윙비트
        Wingbit_1.onAfter(Wingbit_2)
        Wingbit_1.onBefore(core.OptionalElement(FinalFiguration.is_active, Wingbit_Delay_Fig, Wingbit_Delay, name = "변신시"))
        Wingbit_2.onBefore(core.OptionalElement(FinalFiguration.is_active, Wingbit_Delay_Fig, Wingbit_Delay, name = "변신시"))

        # 인퍼널 브레스
        InfernalBreath.onAfter(InfernalBreath_Tile)

        # 프로미넌스
        Prominence_Dummy.onAfter(core.OptionalElement(FinalFiguration.is_active, Prominence_Fig, Prominence, name = "변신시"))
        
        # 드라코 슬래셔
        DrakeSlasher.onAfter(DrakeSlasher_Projectile)
        DrakeSlasher_Fig.onAfter(DrakeSlasher_Fig_Projectile)
        DrakeSlasher_Dummy.onAfter(core.OptionalElement(FinalFiguration.is_active, DrakeSlasher_Fig, DrakeSlasher, name = "변신시"))
        
        # 기가 슬래셔
        GigaSlasher_Dummy = core.OptionalElement(FinalFiguration.is_active, GigaSlasher_Fig, GigaSlasher, name = "변신시")
        
        # 기본공격 - 드라코 슬래셔 / 기가 슬래셔 분기
        BasicAttack = core.DamageSkill('기본 공격',0,0,0).wrap(core.DamageSkillWrapper)
        BasicAttack.onAfter(core.OptionalElement(DrakeSlasher_Dummy.is_available, DrakeSlasher_Dummy, GigaSlasher_Dummy, name = "드라코 슬래셔 충전시"))

        # 윌 오브 소드:스트라이크
        WillOfSwordStrike.onAfter(WillOfSwordStrike_Explode)
        WillOfSwordStrike_Fig.onAfter(WillOfSwordStrike_Fig_Explode)
        WillOfSwordStrike_Dummy.onAfter(core.OptionalElement(FinalFiguration.is_active, WillOfSwordStrike_Fig, WillOfSwordStrike, name = "변신시"))
        
        DrakeSlasherReset = core.StackSkillWrapper(core.BuffSkill('드라코 슬래셔 - 재사용 초기화', 0, 0), 3)
        DrakeSlasher_Dummy.onAfter(core.OptionalElement(partial(DrakeSlasherReset.judge, 1, 1), DrakeSlasher_Dummy.controller(1.0, 'reduce_cooltime_p')))
        DrakeSlasher_Dummy.onAfter(DrakeSlasherReset.stackController(-1))
        WillOfSwordStrike_Dummy.onAfter(DrakeSlasherReset.stackController(3))
        
        # 어드밴스드 윌 오브 소드
        AdvancedWillOfSword_Opt = core.OptionalElement(FinalFiguration.is_active, AdvancedWillOfSword_Fig, AdvancedWillOfSword, name = "변신시")
        AdvancedWillOfSword_Dummy.onAfter(core.OptionalElement(WillOfSwordStrike_Dummy.is_available, WillOfSwordStrike_Dummy, AdvancedWillOfSword_Opt, name = "윌오소스 사용 가능시"))
        
        # 오라 웨폰
        auraweapon_builder = warriors.AuraWeaponBuilder(vEhc, 1, 1)
        for sk in [GigaSlasher, GigaSlasher_Fig, DrakeSlasher, DrakeSlasher_Projectile, DrakeSlasher_Fig, DrakeSlasher_Fig_Projectile]:
            auraweapon_builder.add_aura_weapon(sk)
        AuraWeaponBuff, AuraWeapon = auraweapon_builder.get_buff()
        
        # 쿨 초기화
        for sk in [AdvancedWillOfSword_Dummy, InfernalBreath, SoulContract]:
            MajestyOfKaiser.onAfter(sk.controller(1, "reduce_cooltime_p"))
        
        # 조상님
        GuardianOfNova_1.onAfters([GuardianOfNova_2, GuardianOfNova_3])
        
        # 스택량 계산
        for sk, incr in [[DrakeSlasher_Dummy, 5],
                            [GigaSlasher, 5],
                            [AdvancedWillOfSword_Opt, 60],
                            [InfernalBreath, 40],
                            [Prominence_Dummy, 50]]:
            sk.onAfter(MorphGauge.stackController(incr))
        
        Wingbit_1.onTick(MorphGauge.stackController(1))
        Wingbit_2.onTick(MorphGauge.stackController(1))
        
        for sk in [WillOfSwordStrike_Dummy, DrakeSlasher_Dummy]:
            sk.protect_from_running()
    
        return(BasicAttack,
                [globalSkill.maple_heros(chtr.level, combat_level=self._combat), globalSkill.useful_sharp_eyes(),
                    RegainStrenth, BlazeUp, FinalFiguration, MajestyOfKaiser, FinalTrance, AuraWeaponBuff, AuraWeapon, MorphGauge,
                    SoulContract] +\
                [AdvancedWillOfSword_Dummy] +\
                [Wingbit_1, Wingbit_2, GuardianOfNova_1, GuardianOfNova_2, GuardianOfNova_3] +\
                [WillOfSwordStrike_Dummy, DrakeSlasher_Dummy, InfernalBreath, InfernalBreath_Tile, Petrified, Prominence_Dummy, Phanteon] +\
                [BasicAttack])
